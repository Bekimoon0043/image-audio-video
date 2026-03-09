import os
import tempfile
import shutil
import logging
import traceback
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from .processor import create_video

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Image+Audio to Video")
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = tempfile.mkdtemp()

def cleanup_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/create-video")
async def create_video_endpoint(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    audio: UploadFile = File(...)
):
    logger.info(f"Received request: image={image.filename}, audio={audio.filename}")

    if not image.content_type.startswith("image/"):
        raise HTTPException(400, "Image file must be an image")
    if not audio.content_type.startswith("audio/"):
        raise HTTPException(400, "Audio file must be an audio file")

    image_path = os.path.join(UPLOAD_DIR, f"img_{os.urandom(4).hex()}_{image.filename}")
    audio_path = os.path.join(UPLOAD_DIR, f"aud_{os.urandom(4).hex()}_{audio.filename}")
    output_path = os.path.join(UPLOAD_DIR, f"video_{os.urandom(4).hex()}.mp4")

    try:
        # Write uploaded files
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)

        logger.info(f"Files saved: {image_path}, {audio_path}")

        # Generate the video
        create_video(image_path, audio_path, output_path)
        logger.info(f"Video created: {output_path}")

        # Clean up input files
        cleanup_file(image_path)
        cleanup_file(audio_path)

        background_tasks.add_task(cleanup_file, output_path)

        return FileResponse(output_path, media_type="video/mp4", filename="output.mp4")
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        logger.error(traceback.format_exc())
        # Clean up any files that might have been created
        cleanup_file(image_path)
        cleanup_file(audio_path)
        cleanup_file(output_path)
        raise HTTPException(500, f"Video creation failed: {str(e)}")
