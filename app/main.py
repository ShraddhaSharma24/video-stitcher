import os
import shutil
import tempfile
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import subprocess

from .stitching import VideoStitcher

app = FastAPI(title="Video Stitching API")

stitcher = VideoStitcher()

@app.get("/")
async def root():
    return {"message": "Video Stitching API is up!"}

@app.get("/health")
async def health():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return {"status": "ok", "ffmpeg": True}
    except:
        return {"status": "ok", "ffmpeg": False}

@app.post("/stitch")
async def stitch_videos(files: List[UploadFile] = File(...), method: str = "concat"):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Minimum 2 videos needed")

    temp_dir = tempfile.mkdtemp()
    video_paths = []
    try:
        for i, file in enumerate(files):
            file_path = os.path.join(temp_dir, f"video_{i}.mp4")
            with open(file_path, "wb") as f:
                f.write(await file.read())
            video_paths.append(file_path)

        output_path = os.path.join(stitcher.output_dir, "stitched.mp4")

        result = stitcher.stitch_videos_ffmpeg(video_paths, output_path, method)
        return FileResponse(result, media_type="video/mp4")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

