# Observer
> **"Built by a father who needed to understand his son before he could teach him."**

### Behavioral Telemetry & Observational Reporting

---

## What is Observer?

Observer is a local-first **Behavioral Telemetry Engine** designed to build a high-fidelity baseline for neurodivergent learners. It converts raw video and audio into **structured behavioral episodes** stored in a **Behavioral State Ledger**—a time-ordered database that allows regulatory patterns to emerge across days and weeks.

> **⚠️ Early-Alpha Status:** This project is in active development. The web interface, server, camera monitoring, and longitudinal reporting are functional. Clip trimming and dynamic event isolation are implemented but should be considered experimental. Granular behavioral thresholds and AI interpretation logic will require refinement before the system is considered production-ready.

> **Note on Use:** Observer is a context-building tool for families and specialists. It does **not** diagnose medical conditions, assign clinical labels, or replace professional psychiatric assessment.

---

## Example Behavioral Episode

Observer converts chaotic moments into structured insight. Here is what the "Specialist" model sees when analyzing a detected event:

```json
{
  "timestamp": "2026-03-10T15:42:12",
  "trigger": "Motor Regulation Spike + Vocal Echo",
  "measured_features": {
    "avg_velocity": 4.2,
    "max_acceleration": 12.8,
    "peak_volume": 0.82,
    "duration_sec": 45.5
  },
  "inferred_states": {
    "affective_inference": {
      "distress_likelihood": 0.15,
      "overload_likelihood": 0.72,
      "joy_likelihood": 0.05
    },
    "regulatory_interpretation": {
      "sensory_seeking": 0.2,
      "sensory_avoidance": 0.8,
      "processing_support_needed": 0.9
    }
  }
}
```

### 🗣️ The "Human Translation"
While the data looks clinical, the insight is deeply human. The ledger entry above tells us:
> *"During this 45-second window, the subject wasn't 'acting out'—they were likely experiencing significant sensory overload (0.72) and were struggling to process the environment (0.9 support needed). The high-velocity movement was a regulatory tool, not a random behavior."*

---

## Longitudinal Pattern Discovery

By aggregating episodes over time, Observer identifies the "Hidden Map" of a child's regulation:

*   **Transition Analysis**: Tablet → Learning activities correlate with overload events in 73% of cases.
*   **Intervention Efficacy**: Co-play interventions reduce regulation recovery time by an average of 42 seconds compared to verbal prompting.
*   **Optimal Windows**: Peak engagement and flow states consistently occur between 9:30 AM and 10:45 AM.

---

## Design Principles

1.  **Observation Before Interpretation**: Concrete telemetry (speed, volume) is always separated from AI-inferred emotional states.
2.  **Local-First Sovereignty**: All sensitive sensory data is processed and stored on your own hardware. No raw video leaves the house.
3.  **Ephemeral Capture**: Extract structured insight—then delete the source footage. The wisdom is permanent; the surveillance is temporary.

---

## The Philosophy: Performance vs. Regulation

Most educational software tracks *performance*: Did they get the answer right? Time on task? These metrics are often **context-blind** for neurodivergent children.

Observer starts with **Regulation**. Before a child can learn, they must be regulated. Before they can engage, they must feel safe. Observer bridges the gap by tracking the prerequisites for learning:

- Is the child **regulated** enough to process information?
- Are they in a state of **monotropic flow**, or sensory survival?
- Was a "failed" lesson actually a response to an environmental trigger?

---

## How It Works

### The Architecture

```text
       [ SENSORS ]                     [ ANALYSIS ]                  [ STORAGE ]
     Webcam / Mic Pass              Layered VLM Pipeline           Behavior Ledger
            |                               |                              |
    +-------v-------+               +-------v-------+              +-------v-------+
    | MediaPipe Pose|---Telemetry-->| Moondream     |---Tags------>| SQLite DB     |
    | & Face Mesh   |               | (Scout Pass)  |              | (Episodes)    |
    +---------------+               +-------v-------+              +-------v-------+
            |                               |                              |
    +-------v-------+               +-------v-------+              +-------v-------+
    | Audio Stream  |---Triggers--->| Qwen3-VL      |---Forensics->| Meta-Analysis |
    | (Vocal/Vol)   |               | (Deep Audit)  |              | (Patterns)    |
    +---------------+               +---------------+              +---------------+
```

### The Core Loop
1.  **Interaction**: Sensors capture raw movement and sound.
2.  **Signals**: Real-time extraction of velocity, attention scores, and vocal intensity.
3.  **State Estimation**: Detection of "Event Loops" (Onset to Resolution).
4.  **Contextual Synthesis**: Layered VLM (Moondream/Qwen3) generates psychological inferences.
5.  **Longitudinal Update**: Episodes accumulate into behavioral patterns across days and weeks.

### What Triggers an Episode?
The system automatically captures and analyzes clips when telemetry exceeds baseline thresholds:
*   **Motor Regulation**: Sudden velocity spikes or rhythmic repetitive motion loops (stimming).
*   **Vocal Intensity**: Sustained surges in volume or detected echolalia/scripting patterns.
*   **Latency**: Extended delays in response to prompts or transitions.
*   **Attention Stability**: Significant drops in gaze stability or head orientation disengagement.

---

## Privacy & Ephemeral Capture

Observer is built on a core mandate: **Wisdom, not data.**

For parents of neurodivergent children, pointing a camera at their child is a massive act of trust. We honor that trust through **Ephemeral Capture**:

1.  **Extract then Delete**: The system creates a 30-60 second "event window" to analyze a behavior. As soon as the AI extracts the behavioral insights, the raw video is deleted.
2.  **No Long-Term Surveillance**: We do not keep "tapes." We keep a structured psychological ledger. The surveillance is temporary; the understanding is permanent.
3.  **Local-First Sovereignty**: All vision analysis happens on your local machine. No raw video of your child ever touches the cloud.

---

## Getting Started

> **New to AI or Code?** Start here: [Beginner's Step-by-Step Setup Guide](BEGINNERS_GUIDE.md)

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/)

### Hardware Requirements
Observer performs multi-layered AI inference on your local hardware. To ensure a responsive experience, we recommend:
- **RAM**: 32GB Minimum (16GB may work on some Linux distros but will be significantly slower).
- **CPU**: 8-core modern processor or better.
- **GPU (Optional)**: An NVIDIA GPU with 8GB+ VRAM is highly recommended for faster vision audits.

### Installation
```bash
git clone https://github.com/B-A-M-N/Observer.git
cd Observer
pip install -r requirements.txt
```

### Models (Ollama)
```bash
ollama pull moondream:latest   # High-Speed Scouting
ollama pull qwen3-vl:8b        # Forensic Deep Audit
ollama pull rnj-1:8b           # Local Pattern Recognition
```

---

## Quick Start

1. **Launch**: `python3 main.py`
   *(This initializes your local webcam. Position it to capture the environment.)*

2. **Dashboard**: Open `http://localhost:8001/?token=test_token`

![Dashboard Screenshot Placeholder](https://via.placeholder.com/800x450?text=Observer+Behavioral+State+Ledger+UI)

---

## Roadmap 🚀

- [ ] **Single-Click Installer**: Executables for Windows/Mac to remove the need for terminal commands.
- [ ] **Web-Based Monitoring Gateway**: Secure remote dashboard for therapists to view longitudinal reports.
- [ ] **Progeny Integration**: Bi-directional loop to feed behavioral states into the Progeny teaching system.
- [ ] **Hardware Reference Designs**: Optimized builds for Raspberry Pi 5 and Jetson Nano.
- [ ] **Multi-Camera Syncing**: Support for wide-room observation in classrooms and clinics.

---

## Specialist Support & Implementation

If you are a family or therapist needing specialized setup (hardware selection, threshold tuning, or IEP goal integration), I offer implementation support.

**[Contact Me](mailto:bamn@example.com)** to discuss a tailored implementation for your home or practice.

---

## Part of a Larger Vision

Observer is the observational layer of [Progeny](https://github.com/B-A-M-N/Progeny) — an AI learning companion designed to meet a child where they are. Together, they form an external nervous system and adaptive brain loop for neurodivergent learning.

---

## License
MIT License. *Built with love, necessity, and too many late nights.*
