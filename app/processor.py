import subprocess
import os

def create_video(image_path: str, audio_path: str, output_path: str):
    """
    Use FFmpeg to create a video from a static image and an audio track.
    The video duration matches the audio length.
    """
    # Ensure FFmpeg is installed (it is in the Docker image)
    cmd = [
        "ffmpeg",
        "-y",                # overwrite output if exists
        "-loop", "1",        # loop the image
        "-i", image_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",         # stop when the shortest stream ends (audio)
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr}")
    return output_path
