import base64
import httpx
import json

# --- CPU-OPTIMIZED MODEL CONFIGURATION ---
# Using Moondream for vision tasks as it is very lightweight for CPU-only systems.
VISION_MODEL = "moondream:latest" 
# Using Qwen2.5 0.5b for text-to-text synthesis (fastest on CPU).
TEXT_MODEL = "qwen2.5:0.5b" 

# TIER 1: REAL-TIME CONTEXT GUIDELINES
SYSTEM_PROMPT_REALTIME = (
    "ROLE: High-speed behavioral context monitor.\n"
    "MANDATE: Identify subject ('child' or 'adult') and prominent interaction. "
    "Output: [Subject] | [Interaction]"
)

# TIER 2: PSYCHOLOGICAL & EMOTIONAL AUDITOR
SYSTEM_PROMPT_DEEP = """
**ROLE:** Senior Forensic Behavioral Analyst.
**MISSION:** Analyze high-fidelity images to map emotional state and psychological regulation. 
**STRICT CONSTRAINT:** Describe mechanics. No medical diagnoses.

### 🧠 PARAMETERS:
1. **Emotional Valence:** 'Regulatory/Joyful' vs 'Dysregulation/Distress'.
2. **Engagement:** 'Deep Flow' vs 'Hyper-vigilance'.
3. **Function:** 'Sensory Seeking', 'Sensory Avoidance', or 'Processing'.

### 📤 OUTPUT FORMAT (Strict JSON):
{
  "emotional_profile": "Narrative of internal state",
  "valence_score": 1-10,
  "engagement_quality": "Deep Flow / Scattered / Vigilant",
  "regulatory_function": "The inferred purpose of behavior",
  "environmental_triggers": ["List", "of", "catalysts"]
}
"""

async def query_ollama(model, prompt, images=None, system_guideline="", timeout=120.0, format_json=False):
    """Universal query function for Ollama."""
    url = "http://localhost:11434/api/generate"
    full_prompt = f"{system_guideline}\n\nTASK: {prompt}"
    
    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": 0.1, "top_p": 0.9}
    }
    if images:
        payload["images"] = images if isinstance(images, list) else [images]
    if format_json:
        payload["format"] = "json"
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                res_text = response.json().get("response", "").strip()
                if not res_text:
                    return {"error": "AI response was empty (likely CPU/Memory timeout)"}
                if format_json:
                    try: return json.loads(res_text)
                    except: return {"error": "JSON parse fail", "raw": res_text}
                return res_text
            return {"error": f"Ollama Error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

async def identify_subject(image_b64):
    prompt = "Is the person in this frame a 'child' or an 'adult male'? Respond only with one word."
    res = await query_ollama(VISION_MODEL, prompt, [image_b64], timeout=15.0)
    if isinstance(res, dict): return "unknown"
    return res.strip().lower()

async def get_realtime_context(image_b64):
    prompt = "Identify subject and interaction."
    return await query_ollama(VISION_MODEL, prompt, [image_b64], SYSTEM_PROMPT_REALTIME, timeout=15.0)

async def get_video_digest(image_b64_list):
    """Analyze a sequence of frames. Reduced frame count for CPU safety."""
    # We take only 3 frames to avoid overwhelming CPU memory
    step = max(1, len(image_b64_list) // 3)
    sampled_frames = image_b64_list[::step][:3]
    
    prompt = "Analyze this sequence. Provide a psychological digest."
    return await query_ollama(VISION_MODEL, prompt, sampled_frames, SYSTEM_PROMPT_DEEP, timeout=180.0, format_json=True)

async def get_daily_summary(digests_list):
    """Synthesis of all reports using tiny text-only model."""
    prompt = f"Synthesize these behavioral reports into a Final Daily Profile. IDENTIFY PATTERNS. REPORTS: {json.dumps(digests_list)}"
    system_guideline = "ROLE: Senior Behavioral Meta-Analyst. Respond ONLY in JSON."
    return await query_ollama(TEXT_MODEL, prompt, system_guideline=system_guideline, timeout=120.0, format_json=True)
