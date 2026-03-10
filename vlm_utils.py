import base64
import httpx
import json

# --- CPU-OPTIMIZED MODEL CONFIGURATION ---
# Using Moondream for high-speed 'Scouting' and initial tagging.
VISION_MODEL = "moondream:latest" 
# Using Qwen3-VL for 'Forensic' deep audits on isolated clips.
DEEP_AUDIT_MODEL = "qwen3-vl:8b"
# Using rnj-1:8b for 100% local text-to-text synthesis and meta-analysis.
# (Users with lower-end CPUs can swap this for 'rnj-1:8b-cloud' for faster reports).
TEXT_MODEL = "rnj-1:8b" 

# TIER 1: REAL-TIME CONTEXT GUIDELINES (Moondream)
SYSTEM_PROMPT_REALTIME = (
    "ROLE: High-speed behavioral context monitor.\n"
    "MANDATE: Identify subject ('child' or 'adult') and prominent interaction. "
    "Output: [Subject] | [Interaction]"
)

# TIER 2: FORENSIC BEHAVIORAL AUDITOR (Qwen3-VL)
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
                    # Clean potential markdown block formatting
                    if res_text.startswith("```json"):
                        res_text = res_text.replace("```json", "").replace("```", "").strip()
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

async def get_video_digest(image_b64_list, use_deep_audit=False):
    """Analyze a sequence of frames. 
    If use_deep_audit is True, we use the heavier Qwen3-VL model for forensics.
    Otherwise, we use Moondream for a fast pass.
    """
    model = DEEP_AUDIT_MODEL if use_deep_audit else VISION_MODEL
    
    # We take only a few frames to avoid overwhelming CPU memory
    # 3 for Moondream, maybe 5 for Qwen3-VL if memory allows (but staying safe with 3)
    num_frames = 3
    step = max(1, len(image_b64_list) // num_frames)
    sampled_frames = image_b64_list[::step][:num_frames]
    
    prompt = "Analyze this sequence. Provide a psychological digest."
    return await query_ollama(model, prompt, sampled_frames, SYSTEM_PROMPT_DEEP, timeout=300.0, format_json=True)

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
