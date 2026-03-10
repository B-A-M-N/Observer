import base64
import httpx
import json

# --- CPU-OPTIMIZED MODEL CONFIGURATION ---
# Using Moondream for vision tasks as it is very lightweight for CPU-only systems.
VISION_MODEL = "moondream:latest" 
# Using rnj-1:8b-cloud for text-to-text synthesis and meta-analysis.
TEXT_MODEL = "rnj-1:8b-cloud" 

# TIER 1: REAL-TIME CONTEXT GUIDELINES
SYSTEM_PROMPT_REALTIME = (
    "ROLE: High-speed behavioral context monitor.\n"
    "MANDATE: Identify subject ('child' or 'adult') and prominent interaction. "
    "Output: [Subject] | [Interaction]"
)

# TIER 2: PSYCHOLOGICAL & EMOTIONAL AUDITOR
SYSTEM_PROMPT_DEEP = """
**ROLE:** Senior Forensic Behavioral Analyst.
**MISSION:** Analyze high-fidelity images to infer the subject's internal emotional state and regulatory mechanics. 
**STRICT CONSTRAINT:** Describe the *mechanics* of emotion and regulation. Output strictly in JSON format.

### 🧠 INFERENCE TAXONOMY:
1. **Affective Inference:** Map 'distress_likelihood', 'overload_likelihood', and 'joy_likelihood' (0.0 to 1.0).
2. **Regulatory Interpretation:** Identify if the behavior is 'sensory_seeking', 'sensory_avoidance', or 'processing_support_needed'.
3. **Engagement & Attention:** Characterize the flow state (e.g., Monotropism/Deep Flow, scattered, hyper-vigilant). Note gaze stability and social referencing toward others.
4. **Contextual Narrative:** A brief synthesis of the emotional profile during the episode.

### 📤 OUTPUT FORMAT (Strict JSON):
{
  "affective_inference": {
    "joy_likelihood": 0.0-1.0,
    "distress_likelihood": 0.0-1.0,
    "overload_likelihood": 0.0-1.0
  },
  "regulatory_interpretation": {
    "sensory_seeking_likelihood": 0.0-1.0,
    "sensory_avoidance_likelihood": 0.0-1.0,
    "processing_support_likelihood": 0.0-1.0
  },
  "engagement_quality": "string",
  "emotional_profile": "string (prose narrative)",
  "environmental_triggers": ["list", "of", "strings"]
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

async def get_daily_summary(episodes_list):
    """Synthesis of structured episodes into a Meta-Analysis."""
    prompt = f"Analyze these structured behavioral episodes from a single session. IDENTIFY PATTERNS between measured telemetry and inferred emotional states. \n\nEPISODES: {json.dumps(episodes_list)}"
    system_guideline = (
        "ROLE: Senior Behavioral Meta-Analyst.\n"
        "MISSION: Synthesize concrete telemetry (velocity, volume) with inferred psychological states. "
        "Find correlations (e.g., does high volume always correlate with inferred overload?). "
        "Output strictly in JSON format with a 'longitudinal_patterns' key."
    )
    return await query_ollama(TEXT_MODEL, prompt, system_guideline=system_guideline, timeout=120.0, format_json=True)
