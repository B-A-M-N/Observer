# Observer: Behavioral Telemetry & Observational Reporting

Observer is a local-first system designed to solve a specific problem: **How do we give an AI enough context to actually understand how a specific child learns?**

Generic AI models don't understand the nuance of neurodivergent regulation, sensory triggers, or the "Deep Flow" states that precede successful learning. To build an application that truly caters to a child's needs, the AI needs more than just a prompt—it needs a high-fidelity behavioral baseline.

## The Problem

Most educational tools focus on *performance* (did they get the answer right?). They ignore the *prerequisites* for learning:
- **Regulation:** Is the child calm enough to process information?
- **Engagement:** Are they in a state of monotropic flow or hyper-vigilant distraction?
- **Sensory Context:** Was a "failed" lesson actually caused by a loud noise or a difficult transition?

Observer was built to bridge this gap by converting raw lived behavior into a structured "Behavioral State Ledger" that can eventually inform better teaching strategies.

## How it Works

Observer acts as a high-fidelity "nervous system" that monitors and documents behavioral episodes without sacrificing privacy.

### 1. Hard Telemetry (Measured Features)
The system tracks concrete physical data in real-time to remove guesswork:
- **Motor Rhythm:** Uses MediaPipe Pose tracking to distinguish purposeful movement from repetitive regulatory patterns (stimming).
- **Vocal Intensity:** Streams raw audio volume and identifies scripting/echolalia patterns.
- **Latency:** Documentation of how long it takes to respond to prompts or transitions.

### 2. Psychological Mapping (Inferred States)
Using lightweight Vision-Language Models (VLMs), Observer performs a "Deep Audit" of behavioral events:
- **Affective Inference:** Likelihood of Joy, Distress, or Overload.
- **Regulatory Function:** Identifying if a behavior is Sensory Seeking, Sensory Avoidance, or simple Information Processing.
- **Engagement Quality:** Mapping the quality of focus (e.g., Deep Flow vs. Scattered).

### 3. Automated Forensic Editing
To maintain fidelity while respecting privacy, the system:
- Records raw video only during active windows.
- Automatically trims clips to **30 seconds before and after** a detected behavioral trigger.
- **The Purge:** Deletes all raw video files immediately after the text-based structured annotation is saved to the local database.

### 4. Longitudinal Synthesis
Accumulated episodes can be compiled into a "Meta-Analysis" that identifies trends over days and weeks. This provides a map of what helps *this specific child* stay regulated and engaged.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/)
- **CPU-Optimized Models:**
  ```bash
  ollama pull moondream:latest
  ollama pull qwen2.5:0.5b
  ```

### Quick Start
1. **Launch:** `python3 main.py`
2. **Access:** `http://localhost:8001/?token=test_token`
3. **Observation:** The system follows its internal scheduler (Tue-Sun) to start monitoring windows.
4. **Compile:** Use the UI to generate a consolidated longitudinal report from accumulated episodes.

## Privacy Stance
Observer is built on the principle of **"Wisdom, not Data."** No video or audio is stored long-term. Only the structured psychological insights survive the purge, and all analysis is performed locally on your own machine.
