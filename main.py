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
    cursor.execute("CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, start_time TEXT, end_time TEXT, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, timestamp TEXT, type TEXT, context TEXT, data TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS digests (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, timestamp TEXT, summary TEXT, type TEXT)")
    # New: Structured Behavioral Episode Ledger
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            timestamp TEXT,
            trigger_type TEXT,
            measured_features TEXT,  -- Concrete telemetry (JSON)
            inferred_states TEXT,    -- AI annotations (JSON)
            human_notes TEXT         -- Optional corrections
        )
    """)
    conn.commit()
    conn.close()

init_db()
# MediaPipe setup
from mediapipe.python.solutions import pose as mp_pose
from mediapipe.python.solutions import face_mesh as mp_face
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5)
face_mesh = mp_face.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5)

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
    "vocal_history": deque(maxlen=10),
    "telemetry_buffer": [], # Frame-by-frame motor stats
    "vocal_buffer": [],     # Volume levels
    "attention_buffer": []  # Gaze/Head orientation stats
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

# --- BEHAVIORAL GOVERNANCE RULES ---
RULES_CONFIG = {
    "motor_onset_threshold": 1.5,      # Multiplier of baseline velocity for onset
    "motor_resolution_threshold": 1.2, # Multiplier for resolution
    "event_lookback_max": 25.0,        # Max seconds to look back for onset
    "event_lookahead_max": 30.0,       # Max seconds to look ahead for resolution
    "safety_buffer": 5.0,              # Seconds of extra context to add to clips
    "scout_sample_rate": 10.0,         # Seconds between scout pass visual tags
    "deep_audit_frames": 5             # Number of frames to sample for Qwen3-VL
}

async def process_video_segment(video_path, triggers, session_id, segment_type="Baseline"):
    from moviepy import VideoFileClip, concatenate_videoclips
    
    # 1. Extract Full Telemetry for Window Analysis
    motor_stats = session_data["telemetry_buffer"]
    vocal_stats = session_data["vocal_buffer"]
    attn_stats = session_data["attention_buffer"]
    
    # Reset buffers for next segment
    session_data["telemetry_buffer"] = []
    session_data["vocal_buffer"] = []
    session_data["attention_buffer"] = []

    try:
        full_clip = VideoFileClip(video_path)
        duration = full_clip.duration
        fps = 20 # Defined in VideoWriter
        
        # 2. DYNAMIC WINDOW CALCULATION
        # Goal: Find the 'Event Loop' (Pre-onset to Post-resolution)
        final_episodes = []
        
        # If no telemetry triggers, we might want to do a 'Scout Pass' with Moondream
        # to find visual-only triggers.
        if not triggers:
            print("[SCOUT] No telemetry triggers. Running visual scout pass...")
            # Sample every X seconds
            for offset in range(0, int(duration), int(RULES_CONFIG["scout_sample_rate"])):
                frame = full_clip.get_frame(offset)
                _, buffer = cv2.imencode('.jpg', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                img_b64 = base64.b64encode(buffer).decode('utf-8')
                context = await get_realtime_context(img_b64)
                if "interaction" in context.lower() and "none" not in context.lower():
                    triggers.append((offset, f"Visual Scout: {context}"))

        # Consolidate overlapping windows
        windows = []
        for t_offset, label in triggers:
            # DATA-DRIVEN WINDOW CALCULATION
            t_idx = int(t_offset * 30) # Assuming 30fps telemetry
            start_search = max(0, t_idx - int(RULES_CONFIG["event_lookback_max"] * 30)) 
            end_search = min(len(motor_stats), t_idx + int(RULES_CONFIG["event_lookahead_max"] * 30))
            
            # Find baseline (average of first 2s of segment if possible)
            baseline_v = np.mean([s["velocity"] for s in motor_stats[:60]]) if len(motor_stats) > 60 else 0.5
            
            # Find onset: first point where velocity stays above threshold
            onset_offset = 15 # Default
            for i in range(t_idx, start_search, -1):
                if i < len(motor_stats) and motor_stats[i]["velocity"] < baseline_v * RULES_CONFIG["motor_onset_threshold"]:
                    onset_offset = t_offset - (i / 30.0)
                    break
            
            # Find resolution: point where velocity returns to baseline
            resolution_offset = 15 # Default
            for i in range(t_idx, end_search):
                if i < len(motor_stats) and motor_stats[i]["velocity"] < baseline_v * RULES_CONFIG["motor_resolution_threshold"]:
                    resolution_offset = (i / 30.0) - t_offset
                    break
            
            start = max(0, t_offset - onset_offset - RULES_CONFIG["safety_buffer"]) 
            end = min(duration, t_offset + resolution_offset + RULES_CONFIG["safety_buffer"])
            windows.append([start, end, label])

        # Merge overlapping windows
        merged_windows = []
        if windows:
            windows.sort()
            curr = windows[0]
            for i in range(1, len(windows)):
                if windows[i][0] < curr[1] + 5: # 5s gap tolerance
                    curr[1] = max(curr[1], windows[i][1])
                    curr[2] += f" + {windows[i][2]}"
                else:
                    merged_windows.append(curr)
                    curr = windows[i]
            merged_windows.append(curr)

        # 3. LAYERED ANALYSIS (Moondream Scouting -> Qwen3-VL Forensic)
        for start, end, label in merged_windows:
            print(f"[WINDOW] Isurating: {start:.1f}s to {end:.1f}s | Reason: {label}")
            sub_clip = full_clip.subclipped(start, end)
            
            # Temporary path for the isolated clip
            tmp_sub_path = video_path.replace(".mp4", f"_event_{start:.0f}.mp4")
            sub_clip.write_videofile(tmp_sub_path, codec="libx264", audio=False)
            
            # Sample frames for Qwen3-VL Forensic Audit
            cap = cv2.VideoCapture(tmp_sub_path)
            frames = []
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames > 0:
                # Sample X frames for deep audit
                num_frames = RULES_CONFIG["deep_audit_frames"]
                for i in range(num_frames):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, int(i * (total_frames / num_frames)))
                    ret, frame = cap.read()
                    if ret:
                        _, buffer = cv2.imencode('.jpg', frame)
                        frames.append(base64.b64encode(buffer).decode('utf-8'))
            cap.release()

            # LAYER 2: Qwen3-VL Deep Forensic Audit
            inferred_states = await get_video_digest(frames, use_deep_audit=True)
            
            # Aggregate measured features for THIS specific window
            start_idx = int(start * 30)
            end_idx = int(end * 30)
            win_motor = motor_stats[start_idx:end_idx]
            win_vocal = vocal_stats[start_idx:end_idx]
            
            measured_features = {
                "avg_velocity": float(np.mean([s["velocity"] for s in win_motor])) if win_motor else 0,
                "max_acceleration": float(np.max([s["acceleration"] for s in win_motor])) if win_motor else 0,
                "avg_volume": float(np.mean(win_vocal)) if win_vocal else 0,
                "peak_volume": float(np.max(win_vocal)) if win_vocal else 0,
                "duration_sec": end - start
            }

            # 4. Store in Behavioral Episode Ledger
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO episodes (session_id, timestamp, trigger_type, measured_features, inferred_states)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, datetime.datetime.now().isoformat(), label, 
                  json.dumps(measured_features), json.dumps(inferred_states)))
            conn.commit()
            conn.close()
            
            if os.path.exists(tmp_sub_path): os.remove(tmp_sub_path)

        full_clip.close()
        if os.path.exists(video_path): os.remove(video_path)
        print(f"[PURGE] Cleanup complete. Layered Analysis applied.")
        
    except Exception as e:
        print(f"[ERROR] Process failed: {e}")
        import traceback
        traceback.print_exc()


@app.get("/compile-report")
async def compile_report():
    """Manual compile: synthesizes all accumulated structured episodes."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, trigger_type, measured_features, inferred_states FROM episodes ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows: return JSONResponse(content={"error": "No behavioral episodes accumulated yet."})
    
    episodes = []
    for r in rows:
        episodes.append({
            "time": r[0],
            "trigger": r[1],
            "measured": json.loads(r[2]),
            "inferred": json.loads(r[3])
        })
    
    # Meta-Analysis across all structured episodes
    final_summary = await get_daily_summary(episodes)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    report_path = os.path.join(PROFILE_DIR, f"Longitudinal_Report_{timestamp}.json")
    
    report_data = {
        "generated_at": datetime.datetime.now().isoformat(),
        "meta_analysis": final_summary,
        "structured_episodes": episodes
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
                            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            # Pose
                            pose_res = pose.process(rgb_frame)
                            if pose_res.pose_landmarks:
                                stats = analyzer.update(pose_res.pose_landmarks.landmark)
                                if session_data["is_recording"]:
                                    session_data["telemetry_buffer"].append(stats)
                            
                            # Attention (Face Mesh)
                            face_res = face_mesh.process(rgb_frame)
                            if face_res.multi_face_landmarks:
                                attn = analyzer.calculate_attention(face_res.multi_face_landmarks[0].landmark)
                                if session_data["is_recording"]:
                                    session_data["attention_buffer"].append(attn)

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

            elif message["type"] == "audio_meta":
                volume = message["payload"]["volume"]
                if is_active and session_data["is_recording"]:
                    session_data["vocal_buffer"].append(volume)

    except WebSocketDisconnect:
        if session_data["video_writer"]: session_data["video_writer"].release()

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
