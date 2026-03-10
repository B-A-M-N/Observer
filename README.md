# Observer: Autonomous Behavioral & Psychological Insight Engine

Observer is a local-first, privacy-centric computer vision and audio analysis system designed to map human behavioral patterns, emotional valence, and regulatory states in real-time.

While originally developed as the "sensory nervous system" for the **Progeny (Bitling)** project, Observer is a standalone engine capable of high-fidelity behavioral auditing for any context requiring deep psychological insight without compromising privacy.

## What Observer Does

Observer transforms raw video and audio into a structured psychological map by combining real-time telemetry with Large Vision-Language Models (VLMs).

### 1. High-Fidelity Signal Tracking
- **Motor Regulation Mapping:** Uses MediaPipe Pose tracking and FFT frequency analysis to distinguish between purposeful movement and repetitive regulatory patterns (stimming).
- **Vocal Contextualization:** Monitors speech-to-text streams to identify echolalia, scripting, and vocal intensity shifts.
- **Subject Intelligence:** Automatically distinguishes between subjects (e.g., Child vs. Adult) to apply context-specific analysis logic.

### 2. Automated Forensic Editing
The system doesn't just record; it edits.
- **Trigger-Based Slicing:** When a behavioral or vocal event is detected, the system automatically preserves the **30 seconds before and 30 seconds after** the trigger.
- **Context Preservation:** This ensure the "Antecedent" (the trigger) and the "Resolution" are captured with full video and audio fidelity.
- **The Highlight Reel:** Multiple events are stitched into a single, high-density clip for AI annotation.

### 3. Psychological & Emotional Annotation
Observer uses optimized VLMs (like Moondream and Qwen-VL) to perform a "Deep Audit" of captured events:
- **Emotional Valence:** Maps states from Regulatory/Joyful to Dysregulation/Distress.
- **Engagement Quality:** Distinguishes between "Deep Flow" (Monotropism) and Hyper-vigilance.
- **Regulatory Function:** Identifies the *purpose* of behaviors (Sensory Seeking, Sensory Avoidance, or Processing).

### 4. Privacy-First Architecture (The Purge)
Observer is built on a "Wisdom, not Data" philosophy:
- **Immediate Purge:** Raw video files and trimmed clips are **deleted permanently** as soon as the AI completes its text-based annotation.
- **Local-Only:** No data ever leaves the local machine. The system saves only the "wisdom"—the psychological report—to the local database.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running.
- **Required Models (CPU-Optimized):**
  ```bash
  ollama pull moondream:latest
  ollama pull qwen2.5:0.5b
  ```

### Quick Start
1. **Initialize Engine:** Run `python3 main.py`.
2. **Access Interface:** Navigate to `http://localhost:8001/?token=test_token`.
3. **Monitor:** The system follows its internal scheduler to begin autonomous observation windows.
4. **Compile:** Use the "Compile Comprehensive Report" button to synthesize all accumulated segments into a master daily profile.

## Broad Applications
Beyond its core use in neurodivergent-affirming education (Progeny), Observer can be applied to:
- **Developmental Research:** Mapping cognitive profiles over long periods.
- **Therapeutic Baseline Building:** Providing objective, high-fidelity data for clinicians.
- **Self-Reflective Tools:** Helping individuals understand their own sensory and emotional triggers.
