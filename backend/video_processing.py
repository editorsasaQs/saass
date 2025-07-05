import json
import os
import subprocess
from uuid import uuid4

import whisper

from .ai_scene_planning import get_scene_plan
from .config import OUTPUT_DIR, UPLOAD_DIR


def _status_path(job_dir: str) -> str:
    return os.path.join(job_dir, "status.json")


def _write_status(job_dir: str, status: str, **extra):
    data = {"status": status, **extra}
    with open(_status_path(job_dir), "w") as f:
        json.dump(data, f)


def process_video(job_id: str, target_format: str = "youtube"):
    """Main processing pipeline for a given job ID."""
    job_dir = os.path.join(UPLOAD_DIR, job_id)
    tmp_dir = os.path.join(job_dir, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    try:
        # 1. Transcribe voiceover
        _write_status(job_dir, "processing", step="transcription")
        voiceover_path = os.path.join(job_dir, "voiceover.mp3")
        model = whisper.load_model("small")
        transcription = model.transcribe(voiceover_path)
        transcript_text = transcription.get("text", "")

        # 2. Scene planning via Gemini
        _write_status(job_dir, "processing", step="scene_planning")
        scene_plan = get_scene_plan(transcript_text)
        with open(os.path.join(job_dir, "scene_plan.json"), "w") as f:
            json.dump(scene_plan, f, indent=2)

        # 3. Cut scenes & insert transitions
        _write_status(job_dir, "processing", step="video_editing")
        raw_video = os.path.join(job_dir, "video.mp4")
        segments = []
        for idx, scene in enumerate(scene_plan):
            out_path = os.path.join(tmp_dir, f"scene_{idx}.mp4")
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                raw_video,
                "-ss",
                scene["start"],
                "-to",
                scene["end"],
                "-c",
                "copy",
                out_path,
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            segments.append(out_path)

            # Append transition if provided
            if tid := scene.get("transition_id"):
                t_src = os.path.join(job_dir, "transitions", tid)
                if os.path.exists(t_src):
                    segments.append(t_src)

        concat_file = os.path.join(tmp_dir, "concat.txt")
        with open(concat_file, "w") as cf:
            for seg in segments:
                cf.write(f"file '{seg}'\n")

        combined_video = os.path.join(tmp_dir, "combined.mp4")
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                concat_file,
                "-c",
                "copy",
                combined_video,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # 4. Generate subtitles (.srt)
        srt_path = os.path.join(tmp_dir, "subs.srt")
        with open(srt_path, "w") as srt:
            for idx, scene in enumerate(scene_plan, start=1):
                srt.write(f"{idx}\n")
                srt.write(f"{scene['start'].replace('.', ',')} --> {scene['end'].replace('.', ',')}\n")
                srt.write(f"{scene['subtitle']}\n\n")

        # 5. Overlay logo & subtitles
        logo_path = os.path.join(job_dir, "logo.png")
        logo_subbed = os.path.join(tmp_dir, "logo_subs.mp4")
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                combined_video,
                "-i",
                logo_path,
                "-filter_complex",
                "[0:v][1:v]overlay=10:10,subtitles=" + srt_path,
                "-c:v",
                "libx264",
                "-c:a",
                "copy",
                logo_subbed,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # 6. Mix background music with voiceover
        voiceover_path = os.path.join(job_dir, "voiceover.mp3")
        bgm_path = os.path.join(job_dir, "bgm.mp3")
        final_video = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                logo_subbed,
                "-i",
                voiceover_path,
                "-i",
                bgm_path,
                "-filter_complex",
                "[1:a]volume=1[a1];[2:a]volume=0.3[a2];[a1][a2]amix=inputs=2:duration=first[aout]",
                "-map",
                "0:v",
                "-map",
                "[aout]",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                final_video,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        _write_status(job_dir, "completed", output=final_video)
    except Exception as exc:
        _write_status(job_dir, "error", message=str(exc))