# EditGenius AI

EditGenius AI is a lightweight SaaS-style tool that automatically edits raw video footage into polished content with cuts, transitions, subtitles, logo overlay, and audio mixing.

## Features

- Upload raw video, voice-over, background music, logo, and custom transition clips.
- AI scene planning powered by **Gemini Pro**.
- Automatic subtitle generation + styling.
- Logo overlay (top-left).
- Background music mixed with voice-over at configurable volume.
- Export to YouTube (16:9) or Reel (9:16) formats.

## Tech Stack

- **Backend**: Python (FastAPI) + FFmpeg + Whisper + Gemini Pro
- **Frontend**: HTML + TailwindCSS + Vanilla JS

## Quick Start

1. Clone repository and `cd` into it.
2. Install Python dependencies:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```
3. Ensure FFmpeg is installed and reachable in `$PATH`.
4. Export Gemini API key (optional – a default key is baked in for demo):
   ```bash
   export GEMINI_API_KEY="YOUR_KEY"
   ```
5. Start the server:
   ```bash
   uvicorn backend.main:app --reload
   ```
6. Open browser at `http://localhost:8000` and upload your assets.

## Deployment

The app is fully self-contained; you can deploy on Render, Railway, or any container platform. Example Dockerfile is left as an exercise.