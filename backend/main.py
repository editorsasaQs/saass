import json
import os
import uuid

from fastapi import BackgroundTasks, FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import BASE_DIR, OUTPUT_DIR, UPLOAD_DIR
from .video_processing import process_video

app = FastAPI(title="EditGenius AI")

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
    """Receive user files and enqueue processing job."""

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