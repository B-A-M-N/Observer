# Observer
### Behavioral Telemetry & Observational Reporting

> *Built by a father who needed to understand his son before he could teach him.*

---

## Why This Exists

Most educational AI starts with content. Lesson plans. Curriculum. Correct answers.

This one starts somewhere else.

Before my son can learn anything, he needs to be **regulated**. Before he can engage, he needs to feel **safe**. Before any tool can help him, it has to *understand him* — not the average autistic child, not a clinical profile, not a dataset. Him. Specifically him. On this day. In this moment.

Observer was built to solve that problem.

It is the sensory nervous system for [Progeny](https://github.com/B-A-M-N/Progeny) — an AI learning companion I'm building for my son. But it works as a standalone system for any family, therapist, or educator who needs a high-fidelity behavioral baseline for a neurodivergent child.

The core idea is simple: **you can't teach a child you don't understand, and you can't understand a child you haven't watched.**

---

## The Problem With Every Other Tool

Most educational software tracks *performance*. Did they get the answer right? How many problems completed? Time on task?

These metrics are useless — sometimes actively harmful — if you never ask the prerequisites:

- Is the child **regulated** enough to process new information?
- Are they in a state of **monotropic flow**, or are they in survival mode?
- Was that "failed" lesson actually caused by a loud noise, a difficult transition, or a scratchy sock?

Observer was built to bridge the gap between *what happened* and *why it happened* — converting raw lived behavior into a structured **Behavioral State Ledger** that makes teaching strategies smarter over time.

---

## How It Works

### The Core Loop

```
Interaction / Observation
        ↓
Signals collected
(latency, motor patterns, vocal volume, repetition)
        ↓
State estimation
(regulation + engagement + comprehension)
        ↓
Intervention selection
(explore / practice / stabilize / recover)
        ↓
Contextual synthesis
(environmental triggers + emotional valence)
        ↓
Longitudinal map update
```

### 1. Hard Telemetry — What Can Be Measured
Observer tracks concrete physical data in real time to remove guesswork:

- **Motor Rhythm** — MediaPipe Pose tracking distinguishes purposeful movement from repetitive regulatory patterns (stimming)
- **Attention Tracking** — MediaPipe Face Mesh analyzes head orientation and gaze stability to estimate focus and social referencing
- **Vocal Intensity** — Raw audio volume streaming, with detection of scripting and echolalia patterns
- **Latency** — Response time to prompts and transitions, one of the most reliable regulation signals available

### 2. Scouting & Forensic Deep Audits — What Can Be Inferred
To understand the *why* behind a behavior, Observer uses a **Cascading Vision Pipeline**. Think of this as a "Scout" and a "Specialist" working together:

- **The Scout (Moondream)**: Rapidly scans raw footage to identify simple visual cues—like a specific interaction or a child entering the frame—tagging events that telemetry might miss.
- **The Specialist (Qwen3-VL)**: Once a significant event is isolated, this high-fidelity model performs a "Forensic Audit" on the specific clip to infer deep emotional mechanics:
    - **Affective Inference** — Estimated likelihood of Joy, Distress, or Overload.
    - **Regulatory Function** — Is this behavior Sensory Seeking, Sensory Avoidance, or Information Processing?
    - **Engagement Quality** — Is the child in a state of Deep Flow, or are they scattered, shutdown, or hyper-vigilant?

### 3. The Regulation Model
Unlike systems optimized for performance, Observer's data model is built around the reality of neurodivergent learning cycles:

| Phase | States |
|-------|--------|
| Active Learning | `explore` · `engage` · `advance` |
| Consolidation | `practice` · `stabilize` |
| Recovery | `repair` · `recover` · `rest` |
| Connection | `co_play` |

### 4. Trust Staging
Learning is impossible without safety. Observer tracks progression through foundational trust stages, because **trust is not a nice-to-have — it is the infrastructure**:

`safety` → `familiarity` → `rapport` → `collaboration` → `attachment`

### 5. Dynamic Event Windowing
Observer records only what matters and destroys the rest. We don't just cut clips at random; we use the **Motor Velocity Curve** to automatically detect the **Onset** of a behavioral loop and its **Resolution**. This ensures we capture the full context of a meltdown or a breakthrough without keeping a single second of unnecessary footage.

**The Purge**: All raw video is deleted immediately after the structured forensic annotation is saved. The only thing that survives is the insight.

### 6. Longitudinal Synthesis
Accumulated episodes compile into a Meta-Analysis — a living map of what helps *this specific child* stay regulated, what destabilizes them, and what restores them. Patterns invisible in any single session become clear over days and weeks.

---

## Architectural Philosophy

Observer is built on a core belief: **wisdom, not data**.

The goal is never to accumulate footage. It is never to build a surveillance profile. The goal is to extract structured psychological insight from behavior — then destroy the raw evidence.

Everything processed locally. Nothing stored long-term. The only thing that survives the purge is understanding.

This matters especially for neurodivergent children, who are already over-observed, over-assessed, and chronically reduced to clinical checklists. Observer exists to build a picture that *serves the child* — not a system, not an institution, not a dataset.

---

## Getting Started

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/)

### Models

```bash
ollama pull moondream:latest
ollama pull qwen3-vl:8b
ollama pull rnj-1:8b-cloud
```

Both are CPU-optimized. This runs on normal hardware. No cloud required.

### Quick Start

```bash
# Launch
python3 main.py

# Access
http://localhost:8001/?token=test_token
```

The system follows an internal observation scheduler (Tue–Sun) to manage monitoring windows automatically.

Use the UI to compile a consolidated longitudinal report from accumulated episodes.

> **Roadmap:** We are currently working on a "Single-Click Installer" to remove the need for terminal commands. If you are a parent or therapist who needs this now but isn't comfortable with the setup, see the support section below.

---

## Specialist Support & Implementation

If you are a family, therapist, or educator who needs this tool but doesn't have the technical background to set it up, I offer specialized implementation support. 

As the developer and a parent using this daily, I can help with:
- Custom hardware selection and local setup.
- Tuning the behavioral thresholds for a specific child's profile.
- Integrating the Behavioral Ledger into existing therapy or IEP goals.

**[Contact Me](mailto:bamn@example.com)** to discuss a tailored implementation for your home or practice. 

---

## Privacy Stance

Observer is **local-first by design**. All analysis runs on your machine. No video or audio is stored long-term. Only structured psychological insights survive the purge.

The goal is a tool that families can trust with their most vulnerable moments — and that means building it as if surveillance is the enemy, not the product.

---

## Part of a Larger Vision

Observer is the observational layer of [Progeny](https://github.com/B-A-M-N/Progeny) — an AI learning companion designed specifically for neurodivergent children. Progeny uses the behavioral baseline Observer builds to power a live neuroadaptive teaching system: one that knows when to push, when to back off, and when to just sit with a kid and play.

Together, they represent a single question asked seriously:

**What if AI actually met a child where they are?**

---

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

*Built with love, necessity, and too many late nights.*
