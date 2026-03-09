# Image + Audio to Video

A simple web service that combines one image and one audio file into a video.  
The resulting video shows the image for the entire duration of the audio.

Built with FastAPI and FFmpeg.

## Features

- Web interface for manual uploads
- REST API endpoint for automation (e.g., n8n)
- Returns MP4 video file
- Deployable via Docker (Render-ready)

## API Usage

### `POST /create-video`

Accepts multipart/form-data with two fields:
- `image`: image file (JPEG, PNG, etc.)
- `audio`: audio file (MP3, WAV, etc.)

Returns the generated MP4 video.

## Deployment on Render

1. Fork or clone this repository to your GitHub account.
2. On [Render](https://render.com), create a new **Web Service**.
3. Connect your GitHub repository.
4. Render will automatically detect the `Dockerfile`.
5. Set the service name and region as desired.
6. Click **Create Web Service**.

The service will be live at `https://your-service.onrender.com`.

### Environment Variables

- `PORT` – set automatically by Render. The Dockerfile uses it.

## Local Development

1. Install FFmpeg on your system.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
