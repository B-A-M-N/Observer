import cv2
import numpy as np
import base64
import json
import mediapipe.python.solutions.pose as mp_pose
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import datetime
import asyncio
import time
import sqlite3
import secrets
import os
from collections import deque
from vlm_utils import get_realtime_context, identify_subject, get_video_digest, get_daily_summary
from telemetry_analyzer import TelemetryAnalyzer

app = FastAPI()

# --- STORAGE ---
ACCESS_TOKEN = "test_token"
VIDEO_DIR = "/home/bamn/Observer/raw_segments"
PROFILE_DIR = "/home/bamn/Observer/profiles"
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(PROFILE_DIR, exist_ok=True)

# 1. DATABASE
DB_PATH = "/home/bamn/Observer/progeny_knowledge.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, start_time TEXT, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS digests (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, timestamp TEXT, summary TEXT, type TEXT)")
    conn.commit()
    conn.close()

init_db()

# MediaPipe
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5)

# SESSION STATE
session_data = {
    "id": None,
    "current_subject": None,
    "vlm_queue": asyncio.Queue(maxsize=5),
    "is_recording": False,
    "video_writer": None,
    "current_video_path": None,
    "segment_start_time": None,
    "triggers": [], 
    "vocal_history": deque(maxlen=10)
}

analyzer = TelemetryAnalyzer(fps=30)
LAST_AGGREGATION_TIME = time.time()

def is_active_window():
    now = datetime.datetime.now()
    day = now.weekday()
    hour = now.hour
    minute = now.minute
    time_float = hour + minute/60.0
    active = False
    if day == 1: active = 15.5 <= time_float <= 20.5
    elif 2 <= day <= 4: active = (7.0 <= time_float <= 8.5) or (15.5 <= time_float <= 20.5)
    elif day == 5: active = 7.0 <= time_float <= 20.5
    elif day == 6: active = 7.0 <= time_float <= 12.0
    is_hourly_slot = 0 <= minute < 15
    return active, is_hourly_slot

def start_raw_recording(reason):
    if not session_data["is_recording"]:
        session_data["is_recording"] = True
        session_data["segment_start_time"] = time.time()
        session_data["triggers"] = []
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        session_data["current_video_path"] = os.path.join(VIDEO_DIR, f"seg_{timestamp_str}.mp4")
        session_data["video_writer"] = cv2.VideoWriter(
            session_data["current_video_path"], 
            cv2.VideoWriter_fourcc(*'mp4v'), 20, (640, 480)
        )
        print(f"[REC] STARTING ({reason}): {session_data['current_video_path']}")

async def process_video_segment(video_path, triggers, session_id, segment_type="Baseline"):
    from moviepy import VideoFileClip, concatenate_videoclips
    trimmed_path = None
    try:
        full_clip = VideoFileClip(video_path)
        clips_to_keep = []
        if not triggers:
            clips_to_keep.append(full_clip.subclipped(0, 30))
        else:
            for t_offset, label in triggers:
                start = max(0, t_offset - 30)
                end = min(full_clip.duration, t_offset + 30)
                clips_to_keep.append(full_clip.subclipped(start, end))
        
        if clips_to_keep:
            final_clip = concatenate_videoclips(clips_to_keep)
            trimmed_path = video_path.replace(".mp4", "_trimmed.mp4")
            final_clip.write_videofile(trimmed_path, codec="libx264")
            final_clip.close()
            cap = cv2.VideoCapture(trimmed_path)
            frames = []
            while len(frames) < 12:
                ret, frame = cap.read()
                if not ret: break
                _, buffer = cv2.imencode('.jpg', frame)
                frames.append(base64.b64encode(buffer).decode('utf-8'))
                for _ in range(30): cap.read() 
            cap.release()
            digest = await get_video_digest(frames)
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO digests (session_id, timestamp, summary, type) VALUES (?, ?, ?, ?)",
                           (session_id, datetime.datetime.now().isoformat(), json.dumps(digest), segment_type))
            conn.commit()
            conn.close()
        full_clip.close()
        if os.path.exists(video_path): os.remove(video_path)
        if trimmed_path and os.path.exists(trimmed_path): os.remove(trimmed_path)
        print(f"[PURGE] cleanup done for {segment_type}")
    except Exception as e:
        print(f"[ERROR] failed: {e}")

@app.get("/compile-report")
async def compile_report():
    """Manual compile: synthesizes all accumulated digests."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, summary, type FROM digests ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows: return JSONResponse(content={"error": "No reports accumulated yet."})
    
    digests = [json.loads(r[1]) for r in rows]
    final_summary = await get_daily_summary(digests)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    report_path = os.path.join(PROFILE_DIR, f"Comprehensive_Report_{timestamp}.json")
    
    report_data = {
        "generated_at": datetime.datetime.now().isoformat(),
        "meta_analysis": final_summary,
        "individual_segments": [{"time": r[0], "type": r[2], "content": json.loads(r[1])} for r in rows]
    }
    
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)
        
    return JSONResponse(content=report_data)

async def vlm_worker():
    while True:
        img_b64 = await session_data["vlm_queue"].get()
        try:
            subj = await identify_subject(img_b64)
            session_data["current_subject"] = subj
        finally:
            session_data["vlm_queue"].task_done()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(vlm_worker())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    if token != ACCESS_TOKEN:
        await websocket.close(code=4003)
        return
    global LAST_AGGREGATION_TIME
    await websocket.accept()
    if not session_data["id"]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sessions (start_time, status) VALUES (?, ?)", (datetime.datetime.now().isoformat(), "open"))
        session_data["id"] = cursor.lastrowid
        conn.commit()
        conn.close()

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            is_active, is_hourly_slot = is_active_window()
            is_child = (session_data["current_subject"] == "child")
            now_unix = time.time()
            
            if message["type"] == "frame":
                img_b64 = message["data"].split(",")[1]
                if is_active:
                    if not session_data["vlm_queue"].full():
                        try: session_data["vlm_queue"].put_nowait(img_b64)
                        except: pass
                    if is_hourly_slot and not session_data["is_recording"]:
                        start_raw_recording("Routine Baseline")
                    if is_child or session_data["is_recording"]:
                        nparr = np.frombuffer(base64.b64decode(img_b64), np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        if session_data["is_recording"] and frame is not None:
                            resized = cv2.resize(frame, (640, 480))
                            session_data["video_writer"].write(resized)
                        if is_child:
                            pose_res = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                            if pose_res.pose_landmarks:
                                analyzer.update(pose_res.pose_landmarks.landmark)
                            if now_unix - LAST_AGGREGATION_TIME >= 1.0:
                                _, amp = analyzer.analyze_frequency()
                                if amp > 0.04:
                                    if not session_data["is_recording"]: start_raw_recording("Triggered Segment")
                                    offset = now_unix - session_data["segment_start_time"]
                                    session_data["triggers"].append((offset, "Motor Regulation"))
                                LAST_AGGREGATION_TIME = now_unix
                    if session_data["is_recording"] and (now_unix - session_data["segment_start_time"] >= 900):
                        session_data["video_writer"].release()
                        session_data["is_recording"] = False
                        # Determine type
                        seg_type = "Triggered" if any(t[1] != "Baseline" for t in session_data["triggers"]) else "Baseline"
                        asyncio.create_task(process_video_segment(session_data["current_video_path"], session_data["triggers"], session_data["id"], seg_type))

                await websocket.send_json({"type": "Analysis", "data": {"state": "Active" if is_active else "Standby", "subject": session_data["current_subject"], "recording": session_data["is_recording"]}})

            elif message["type"] == "speech":
                if is_active and is_child:
                    text = message["text"].lower().strip()
                    if text in session_data["vocal_history"]:
                        if not session_data["is_recording"]: start_raw_recording("Triggered Segment")
                        offset = time.time() - session_data["segment_start_time"]
                        session_data["triggers"].append((offset, f"Echolalia: {text}"))
                    session_data["vocal_history"].append(text)

    except WebSocketDisconnect:
        if session_data["video_writer"]: session_data["video_writer"].release()

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
