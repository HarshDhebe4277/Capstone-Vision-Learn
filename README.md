<p align="center">
  <h1 align="center">🎓 Vision-Learn AI</h1>
  <p align="center">
    <strong>AI-powered pedagogical narration engine for visually impaired students</strong>
  </p>
  <p align="center">
    Transforms YouTube lectures, local videos, and PDF/image notes into<br/>
    high-quality, teacher-like audio narrations using Mistral AI + Edge TTS
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Mistral_AI-Pixtral_|_Voxtral-ff6f00?logo=data:image/svg+xml;base64,..." alt="Mistral AI"/>
  <img src="https://img.shields.io/badge/PostgreSQL-15+-336791?logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/LangChain-0.2+-green" alt="LangChain"/>
</p>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Pipeline 1 — Video to Narration](#-pipeline-1--video-to-narration)
- [Pipeline 2 — Notes (PDF/Image) to Narration](#-pipeline-2--notes-pdfimage-to-narration)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [API Endpoints](#-api-endpoints)
- [Setup & Installation](#-setup--installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Methodology](#-methodology)

---

## 🌟 Overview

**Vision-Learn AI** is an end-to-end AI pipeline designed to make educational content accessible to **blind and visually impaired students**. It takes video lectures or PDF/image notes as input and produces **pedagogically-aware audio narrations** — not robotic descriptions, but actual teacher-like explanations with analogies, intuition, and learning hooks.

The system leverages:
- **Mistral AI models** (Pixtral for vision, Voxtral for transcription, Mistral Large for reasoning)
- **LangChain** for AI chain orchestration
- **Edge TTS** for natural-sounding speech synthesis
- **FastAPI** for a production-ready REST API

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎬 **YouTube Pipeline** | Full pipeline: download → transcribe → extract key frames → generate narration → TTS |
| 📄 **Notes Pipeline** | PDF/Image → page extraction → vision-based teaching narration → TTS |
| 🎤 **Pedagogical Narration** | AI teaches like a human teacher — explains WHY, uses analogies, adds interview tips |
| 🔄 **Smart Caching** | Intermediate results cached — re-running skips completed steps |
| ⚡ **Parallel Processing** | Audio chunking + parallel transcription for speed |
| 🛡️ **Rate Limit Handling** | Exponential backoff retry on API rate limits (429) |
| 📦 **Local File Support** | Process local video/audio files directly (no YouTube needed) |
| 🗄️ **PostgreSQL Persistence** | Full database schema for lectures, transcripts, frames, scripts, and audio |

---

## 🏗 Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Vision-Learn AI Backend                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐     ┌──────────────────┐     ┌────────────────┐  │
│  │   FastAPI     │     │  Video Pipeline   │     │ Notes Pipeline │  │
│  │   REST API    │────▶│  (8-step flow)    │     │ (3-step flow)  │  │
│  │              │     │                  │     │                │  │
│  │  /api/pipeline│     │  YouTube/Local    │     │  PDF/Image     │  │
│  │  /api/notes   │────▶│  → Narration MP3  │     │  → Narration   │  │
│  └──────────────┘     └──────────────────┘     └────────────────┘  │
│         │                      │                        │          │
│         ▼                      ▼                        ▼          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Shared Services Layer                      │  │
│  │  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │  │
│  │  │ Mistral │  │ Voxtral  │  │ Pixtral  │  │   Edge TTS   │ │  │
│  │  │ LLM     │  │ STT      │  │ Vision   │  │   Synthesis  │ │  │
│  │  └─────────┘  └──────────┘  └──────────┘  └──────────────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
│         │                                                          │
│         ▼                                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                 PostgreSQL + SQLAlchemy ORM                   │  │
│  │  Users │ Lectures │ Transcripts │ Frames │ Scripts │ Audio   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎬 Pipeline 1 — Video to Narration

Converts YouTube lectures or local video/audio files into pedagogical audio narrations.

### Pipeline Flow

```
Input (YouTube URL / Local File)
        │
        ▼
┌─────────────────────────────────────┐
│ Step 1: Fetch Stream URL +          │   ← yt-dlp (parallel)
│         Download Audio              │   ← ffmpeg for local files
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│ Step 2: Split Audio into N Chunks   │   ← pydub (default: 12 chunks)
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│ Step 3: Parallel Transcription      │   ← Voxtral Mini (Mistral STT)
│         (all chunks concurrently)   │   ← Async parallel execution
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│ Step 4: Select Key Timestamps       │   ← Mistral LLM + LangChain
│         via LLM Analysis            │   ← Identifies important visual moments
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│ Step 5: Extract Frames at           │   ← ffmpeg (parallel extraction)
│         Key Timestamps              │   ← From CDN stream or local file
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│ Step 6: Generate Pedagogical        │   ← Mistral Large (text-only mode)
│         Narration Script            │   ← Transcript + frame context
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│ Step 7: Text-to-Speech Synthesis    │   ← Edge TTS (Microsoft)
│                                     │   ← [PAUSE] markers → 800ms gaps
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│ Step 8: Persist to PostgreSQL       │   ← Optional DB storage
│         (if session provided)       │
└─────────────────────────────────────┘
        │
        ▼
    Output: narration.mp3 + script.txt + transcript.json + frames/
```

### Models Used (Video Pipeline)

| Step | Model | Purpose |
|------|-------|---------|
| Transcription | `voxtral-mini-latest` | Speech-to-text for audio chunks |
| Timestamp Selection | `mistral-small-latest` | Identify key visual moments from transcript |
| Narration Script | `mistral-small-latest` | Generate teaching script (text-only, no images) |
| Speech Synthesis | `en-US-GuyNeural` | Edge TTS voice for audio output |

---

## 📄 Pipeline 2 — Notes (PDF/Image) to Narration

Converts PDF documents or image files of course notes/slides into teacher-like audio narrations.

### Pipeline Flow

```
Input (PDF / JPG / PNG)
        │
        ▼
┌─────────────────────────────────────┐
│ Step 1: Extract Pages as Images     │   ← PyMuPDF (fitz) for PDFs
│         • 100 DPI resolution        │   ← PIL for single images
│         • Max 1024px longest side    │   ← JPEG quality 70 (compressed)
│         • Optimized for API limits   │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│ Step 2: Vision LLM Teaching         │   ← Pixtral 12B (vision model)
│         Narration Generation        │   ← 1 page per API call
│                                     │   ← Continuity context between pages
│         • Teaches concepts          │   ← Exponential backoff retry
│         • Explains WHY              │
│         • Uses analogies            │
│         • Adds interview tips       │
│         • Natural topic bridges     │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│ Step 3: Text-to-Speech Synthesis    │   ← Edge TTS (Microsoft)
│                                     │   ← [PAUSE] markers → 800ms gaps
└─────────────────────────────────────┘
        │
        ▼
    Output: narration.mp3 + script.txt + pages/
```

### Models Used (Notes Pipeline)

| Step | Model | Purpose |
|------|-------|---------|
| Vision Script | `pixtral-12b-2409` | Read page images and generate teaching narration |
| Speech Synthesis | `en-US-GuyNeural` | Edge TTS voice for audio output |

### Pedagogical Narration Quality

The Vision LLM is prompted to teach like an experienced human teacher:

| Aspect | What It Does |
|--------|-------------|
| 🎯 **Teaches, not describes** | Never says "the image shows" — explains concepts directly |
| 🧠 **Explains the WHY** | Builds intuition, not just step-by-step |
| 🌍 **Real-world analogies** | Stack → "like a stack of plates", Queue → "like a ticket counter line" |
| 💡 **Learning hooks** | "This is a classic interview question…", "Common mistake here…" |
| 🔗 **Topic bridges** | Natural transitions between concepts across pages |
| 📝 **Key takeaways** | Summary after each major concept |
| ✂️ **Concise** | 150-250 words per page, zero fluff |

---

## 🛠 Tech Stack

| Category | Technology | Version |
|----------|-----------|---------|
| **Backend Framework** | FastAPI | 0.111.0 |
| **Server** | Uvicorn | 0.29.0 |
| **Language** | Python | 3.11+ |
| **Database** | PostgreSQL | 15+ |
| **ORM** | SQLAlchemy | 1.4.49 |
| **Migrations** | Alembic | 1.11.1 |
| **AI Orchestration** | LangChain | 0.2+ |
| **AI Models** | Mistral AI (Pixtral, Voxtral, Mistral Large) | Latest |
| **TTS Engine** | Microsoft Edge TTS | 6.1+ |
| **Video Processing** | yt-dlp + FFmpeg | Latest |
| **PDF Processing** | PyMuPDF (fitz) | 1.23+ |
| **Image Processing** | Pillow (PIL) | 10.0+ |
| **Audio Processing** | pydub | 0.25+ |

---

## 📁 Project Structure

```
backend/
├── main.py                          # FastAPI application entry point
├── models.py                        # SQLAlchemy ORM models (all tables)
├── database.py                      # Database connection setup
├── requirements.txt                 # Python dependencies
├── alembic.ini                      # Alembic migration config
├── .env.example                     # Environment variables template
│
├── api/                             # REST API layer
│   ├── router.py                    # Central router (registers all controllers)
│   ├── controllers/
│   │   ├── pipeline_controller.py   # /api/pipeline/* endpoints
│   │   ├── notes_controller.py      # /api/notes/* endpoints
│   │   ├── lecture_controller.py     # /api/lectures/* CRUD
│   │   └── audio_controller.py      # /api/audio/* streaming
│   └── schemas/
│       ├── pipeline_schema.py       # Request/response models (pipeline)
│       └── lecture_schema.py        # Request/response models (lectures)
│
├── pipeline/                        # 🎬 VIDEO NARRATION PIPELINE
│   ├── orchestrator.py              # Main 8-step pipeline coordinator
│   ├── chains/
│   │   ├── timestamp_chain.py       # LangChain: select key timestamps from transcript
│   │   └── narration_chain.py       # LangChain: generate pedagogical script
│   ├── services/
│   │   ├── video_downloader.py      # yt-dlp: stream URL + audio download
│   │   ├── audio_chunker.py         # pydub: split audio into N parallel chunks
│   │   ├── transcription_service.py # Voxtral: parallel async transcription
│   │   ├── frame_extractor.py       # ffmpeg: extract frames at key timestamps
│   │   ├── tts_service.py           # Edge TTS: text → speech with [PAUSE] support
│   │   └── local_file_processor.py  # Handle local video/audio file inputs
│   └── utils/
│       ├── cache.py                 # JSON-based pipeline step caching
│       ├── ffmpeg_utils.py          # FFmpeg availability check
│       └── image_utils.py           # Image encoding utilities
│
├── notes_pipeline/                  # 📄 NOTES NARRATION PIPELINE
│   ├── notes_orchestrator.py        # Main 3-step pipeline coordinator
│   ├── chains/
│   │   └── notes_narration_chain.py # Pixtral vision: page → teaching narration
│   └── services/
│       ├── pdf_processor.py         # PyMuPDF: PDF → compressed page images
│       └── image_processor.py       # PIL: normalize single image inputs
│
├── db/                              # Database layer
│   ├── session.py                   # Session factory + get_db dependency
│   ├── base.py                      # Declarative base
│   ├── models/                      # Model definitions (if separate)
│   └── repositories/               # Data access layer
│       ├── lecture_repository.py
│       ├── transcript_repository.py
│       ├── frame_repository.py
│       ├── script_repository.py
│       └── audio_repository.py
│
├── alembic/                         # Database migrations
│   └── versions/                    # Migration scripts
│
└── storage/                         # Generated artifacts (gitignored)
    └── <video_id or note_id>/
        ├── audio/audio.mp3          # Extracted audio
        ├── transcript/transcript.json
        ├── frames/                  # Extracted key frames
        ├── pages/                   # PDF page images (notes pipeline)
        ├── script.txt               # Generated narration script
        └── narration.mp3            # Final TTS audio output
```

---

## 🗄 Database Schema

```
┌──────────────┐     ┌──────────────┐     ┌─────────────────────┐
│    users      │     │   lectures   │     │   processing_jobs   │
├──────────────┤     ├──────────────┤     ├─────────────────────┤
│ id (UUID PK) │◄────│ uploaded_by  │     │ lecture_id (FK)     │
│ email        │     │ id (UUID PK) │◄────│ job_type            │
│ name         │     │ title        │     │ status              │
│ role         │     │ source_type  │     │ attempts            │
│ password_hash│     │ source_url   │     │ result (JSONB)      │
│ is_active    │     │ status       │     └─────────────────────┘
└──────────────┘     │ metadata_    │
                     └──────┬───────┘
                            │
          ┌─────────────────┼─────────────────────┐
          ▼                 ▼                     ▼
┌──────────────┐   ┌──────────────┐   ┌────────────────────┐
│ transcripts  │   │   frames     │   │ pedagogical_scripts│
├──────────────┤   ├──────────────┤   ├────────────────────┤
│ lecture_id   │   │ lecture_id   │   │ lecture_id          │
│ content      │   │ timestamp_s  │   │ version             │
│ segments     │   │ image_path   │   │ content             │
│ model_info   │   │ ocr_text     │   │ sections (JSONB)    │
└──────────────┘   │ features     │   │ generated_by        │
                   └──────┬───────┘   └─────────┬──────────┘
                          ▼                     ▼
                ┌──────────────────┐   ┌──────────────┐
                │ visual_elements  │   │ audio_lectures│
                ├──────────────────┤   ├──────────────┤
                │ frame_id (FK)    │   │ script_id    │
                │ element_type     │   │ tts_voice    │
                │ bbox (JSONB)     │   │ audio_path   │
                │ extracted_text   │   │ duration_s   │
                │ confidence       │   └──────────────┘
                └──────────────────┘
```

---

## 🔌 API Endpoints

### Video Pipeline

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/pipeline/process` | Process a YouTube lecture URL |
| `POST` | `/api/pipeline/process-local` | Process a local video/audio file by path |
| `POST` | `/api/pipeline/upload` | Upload and process a video/audio file |

### Notes Pipeline

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/notes/process` | Upload a PDF/Image and generate narration |

### Other

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI (interactive API docs) |
| `GET` | `/redoc` | ReDoc API documentation |

---

## 🚀 Setup & Installation

### Prerequisites

- **Python 3.11+**
- **PostgreSQL 15+**
- **FFmpeg** (must be in system PATH)
- **Mistral AI API Key** ([Get one here](https://console.mistral.ai/))

### Step 1: Clone the Repository

```bash
git clone https://github.com/<your-username>/vision-learn-ai.git
cd vision-learn-ai/backend
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install FFmpeg

```bash
# Windows (via chocolatey)
choco install ffmpeg

# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

Verify installation:
```bash
ffmpeg -version
```

### Step 5: Setup PostgreSQL Database

```sql
CREATE DATABASE VisionLearn;
```

### Step 6: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/VisionLearn
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_TEXT_MODEL=mistral-small-latest
MISTRAL_VISION_MODEL=pixtral-12b-2409
MISTRAL_TRANSCRIPTION_MODEL=voxtral-mini-latest
```

### Step 7: Run Database Migrations

```bash
alembic upgrade head
```

### Step 8: Start the Server

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at:
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## ⚙ Configuration

All configuration is done via the `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | — | PostgreSQL connection string |
| `MISTRAL_API_KEY` | — | Your Mistral AI API key |
| `MISTRAL_TEXT_MODEL` | `mistral-small-latest` | LLM for timestamp selection & narration |
| `MISTRAL_VISION_MODEL` | `pixtral-12b-2409` | Vision model for image-based narration (MUST be Pixtral) |
| `MISTRAL_TRANSCRIPTION_MODEL` | `voxtral-mini-latest` | Speech-to-text model |
| `STORAGE_PATH` | `./storage` | Directory for pipeline artifacts |
| `AUDIO_CHUNK_COUNT` | `12` | Number of parallel transcription chunks |
| `MAX_FRAME_WORKERS` | `8` | Max parallel ffmpeg frame extraction processes |
| `WHISPER_LANGUAGE` | `en` | Language hint for Voxtral |
| `EDGE_TTS_VOICE` | `en-US-GuyNeural` | TTS voice for narration |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed CORS origins (comma-separated) |

> ⚠️ **Important**: `MISTRAL_VISION_MODEL` MUST be a Pixtral model (e.g., `pixtral-12b-2409`). Standard Mistral text models cannot process images and will cause 429 rate limit errors.

---

## 📖 Usage

### Process a YouTube Lecture

```bash
curl -X POST http://localhost:8000/api/pipeline/process \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

### Process a Local Video/Audio File

```bash
curl -X POST http://localhost:8000/api/pipeline/process-local \
  -H "Content-Type: application/json" \
  -d '{"file_path": "C:/path/to/lecture.mp4"}'
```

### Process PDF/Image Notes

```bash
curl -X POST http://localhost:8000/api/notes/process \
  -F "file=@/path/to/notes.pdf"
```

Or use the **Swagger UI** at http://localhost:8000/docs for interactive testing.

---

## 🔬 Methodology

### 1. Audio Transcription (Video Pipeline)

The audio is split into N chunks (default: 12) and transcribed **in parallel** using Mistral's **Voxtral Mini** model. This approach:
- Reduces wall-clock time by ~10x vs sequential
- Handles long lectures (1-2 hours) without timeouts
- Produces timestamped segments for frame extraction

### 2. Key Frame Selection (Video Pipeline)

A Mistral LLM analyzes the full transcript and identifies **key visual moments** — timestamps where something important appears on screen (new slide, diagram, equation, code example). This is more intelligent than uniform sampling.

### 3. Pedagogical Script Generation

**Video Pipeline**: Uses the full transcript + frame timestamp/reason metadata as text context. No images are sent — avoids vision API rate limits entirely.

**Notes Pipeline**: Uses Pixtral-12B vision model to directly read page images. Each page is processed individually with **continuity context** — the model receives a brief summary of what it taught in the previous page, enabling natural topic transitions and avoiding repetitive introductions.

### 4. Teaching Quality (Notes Pipeline)

The AI is prompted to teach like a **human teacher**, not describe images:

| Traditional Approach | Vision-Learn Approach |
|---------------------|----------------------|
| "The image shows a stack implementation" | "Let me walk you through how a stack works" |
| "The code defines a class called Stack" | "We create a class to group all stack operations together" |
| "The push function adds an element" | "Push is like placing a plate on a stack — last in, first out" |
| "Page 5: Next section" | "Now that we understand stacks, let's combine it with queues" |

### 5. Rate Limit Resilience

The system handles Mistral API rate limits through:
- **Image compression**: 100 DPI, max 1024px, JPEG quality 70
- **Sequential processing**: 1 page per API call (notes pipeline)
- **Exponential backoff**: 10s → 20s → 40s → 80s → 160s retry on 429 errors
- **Smart model selection**: Pixtral for images, Mistral Large for text-only (avoids vision API limits)

### 6. Speech Synthesis

Generated scripts are converted to audio using **Microsoft Edge TTS**:
- Free, no API key required
- Natural-sounding neural voices
- `[PAUSE]` markers in the script are converted to **800ms silence gaps**
- Multiple segments are stitched into a single MP3

---

<p align="center">
  <strong>Built with ❤️ for accessibility in education</strong>
</p>
