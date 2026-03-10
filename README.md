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

### 2. Layered Psychological Mapping — What Can Be Inferred
Observer uses a **Cascading Vision Pipeline** to perform high-fidelity behavioral audits without stalling the CPU:

- **Layer 1: Moondream (Scout Pass)** — Rapidly scans raw footage to identify visual-only triggers and interaction tags.
- **Layer 2: Qwen3-VL (Forensic Specialist)** — Performs a deep "Forensic Audit" of isolated clips to infer:
    - **Affective Inference** — Estimated likelihood of Joy, Distress, or Overload
    - **Regulatory Function** — Is this behavior Sensory Seeking, Sensory Avoidance, or Information Processing?
    - **Engagement Quality** — Deep Flow vs. Scattered vs. Shutdown vs. Vigilant

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
Observer records only what matters and destroys the rest:

- Raw video captured only during active observation windows
- **Dynamic Context Isolation**: Clips are no longer cut at fixed intervals. The system analyzes the **Motor Velocity Curve** to automatically detect the **Onset** (trigger) and **Resolution** (return to baseline) of an event, ensuring the full "event loop" is captured with a safety buffer.
- **The Purge**: all raw video deleted immediately after structured forensic annotation is saved to the local database

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
