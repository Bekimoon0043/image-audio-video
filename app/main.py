import os
import tempfile
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from .processor import create_video

app = FastAPI(title="Image+Audio to Video")
templates = Jinja2Templates(directory="app/templates")

# Use a temporary directory for uploads (Render's /tmp is fine)
UPLOAD_DIR = tempfile.mkdtemp()

def cleanup_file(path: str):
    """Delete a file if it exists (to be used as background task)."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass  # ignore cleanup errors

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the simple upload form."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health():
    """Health check endpoint for Render."""
    return {"status": "ok"}

@app.post("/create-video")
async def create_video_endpoint(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    audio: UploadFile = File(...)
):
    """
    Accept an image and an audio file, then return a generated video.
    """
    # Basic content-type validation (can be extended)
    if not image.content_type.startswith("image/"):
        raise HTTPException(400, "Image file must be an image")
    if not audio.content_type.startswith("audio/"):
        raise HTTPException(400, "Audio file must be an audio file")

    # Save uploaded files to temporary location
    image_path = os.path.join(UPLOAD_DIR, f"img_{os.urandom(4).hex()}_{image.filename}")
    audio_path = os.path.join(UPLOAD_DIR, f"aud_{os.urandom(4).hex()}_{audio.filename}")
    output_path = os.path.join(UPLOAD_DIR, f"video_{os.urandom(4).hex()}.mp4")

    try:
        # Write uploaded files
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)

        # Generate the video
        create_video(image_path, audio_path, output_path)

        # Input files are no longer needed – delete them now
        cleanup_file(image_path)
        cleanup_file(audio_path)

        # Schedule deletion of the output file after the response is sent
        background_tasks.add_task(cleanup_file, output_path)

        # Return the video file
        return FileResponse(output_path, media_type="video/mp4", filename="output.mp4")
    except Exception as e:
        # Clean up any files that might have been created
        cleanup_file(image_path)
        cleanup_file(audio_path)
        cleanup_file(output_path)
        # Log the error (you might want to use proper logging)
        print(f"Error processing: {e}")
        raise HTTPException(500, f"Video creation failed: {str(e)}")
