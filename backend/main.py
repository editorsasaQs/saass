import json
import os
import uuid
from fastapi import HTTPException

from fastapi import BackgroundTasks, FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import BASE_DIR, OUTPUT_DIR, UPLOAD_DIR
from .video_processing import process_video
from .logger import get_logger

app = FastAPI(title="EditGenius AI")
logger = get_logger(__name__)

# Ensure necessary directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount frontend static files
frontend_dir = os.path.join(BASE_DIR, "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse("<script>window.location.href='/frontend/index.html';</script>")


@app.post("/upload")
async def upload(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    voiceover: UploadFile = File(...),
    bgm: UploadFile = File(...),
    logo: UploadFile = File(...),
    transitions: list[UploadFile] = File(...),
    target_format: str = Form("youtube"),
):
    """Receive user files and enqueue processing job with validation."""

    # Basic validations
    allowed_video_ct = {"video/mp4"}
    allowed_audio_ct = {"audio/mpeg", "audio/mp3"}
    allowed_img_ct = {"image/png"}

    if video.content_type not in allowed_video_ct:
        raise HTTPException(status_code=400, detail="Invalid video file type")
    if voiceover.content_type not in allowed_audio_ct:
        raise HTTPException(status_code=400, detail="Invalid voiceover file type")
    if bgm.content_type not in allowed_audio_ct:
        raise HTTPException(status_code=400, detail="Invalid background music file type")
    if logo.content_type not in allowed_img_ct:
        raise HTTPException(status_code=400, detail="Invalid logo file type (PNG required)")
    if target_format not in {"youtube", "reel"}:
        raise HTTPException(status_code=400, detail="target_format must be 'youtube' or 'reel'")

    logger.info("New upload received. target_format=%s transitions=%d", target_format, len(transitions))

    job_id = str(uuid.uuid4())
    job_dir = os.path.join(UPLOAD_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    # Save core assets
    mapping = {
        "video.mp4": video,
        "voiceover.mp3": voiceover,
        "bgm.mp3": bgm,
        "logo.png": logo,
    }
    for fname, ufile in mapping.items():
        with open(os.path.join(job_dir, fname), "wb") as dst:
            dst.write(await ufile.read())

    # Save transitions
    t_dir = os.path.join(job_dir, "transitions")
    os.makedirs(t_dir, exist_ok=True)
    for tfile in transitions:
        with open(os.path.join(t_dir, tfile.filename), "wb") as dst:
            dst.write(await tfile.read())

    # Initial status
    with open(os.path.join(job_dir, "status.json"), "w") as st:
        json.dump({"status": "queued"}, st)

    background_tasks.add_task(process_video, job_id, target_format)
    return {"job_id": job_id}


@app.get("/status/{job_id}")
async def status(job_id: str):
    job_dir = os.path.join(UPLOAD_DIR, job_id)
    status_path = os.path.join(job_dir, "status.json")
    if not os.path.exists(status_path):
        return JSONResponse({"error": "job not found"}, status_code=404)
    with open(status_path) as f:
        return JSONResponse(json.load(f))


@app.get("/download/{job_id}")
async def download(job_id: str):
    video_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")
    if not os.path.exists(video_path):
        return JSONResponse({"error": "not ready"}, status_code=404)
    return FileResponse(video_path, media_type="video/mp4", filename=f"editgenius_{job_id}.mp4")