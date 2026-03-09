import subprocess
import logging

logger = logging.getLogger(__name__)

def create_video(image_path: str, audio_path: str, output_path: str):
    """
    Use FFmpeg to create a video from a static image and an audio track.
    The video duration matches the audio length. Scales image to even dimensions.
    """
    cmd = [
        "ffmpeg",
        "-y",                # overwrite output if exists
        "-loop", "1",        # loop the image
        "-i", image_path,
        "-i", audio_path,
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",  # ensure dimensions are even
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",         # stop when the shortest stream ends (audio)
        output_path
    ]
    logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 min timeout
        if result.returncode != 0:
            logger.error(f"FFmpeg stderr: {result.stderr}")
            raise RuntimeError(f"FFmpeg error: {result.stderr}")
        return output_path
    except subprocess.TimeoutExpired:
        logger.error("FFmpeg process timed out after 300 seconds")
        raise RuntimeError("FFmpeg process timed out")
    except Exception as e:
        logger.error(f"Unexpected error in FFmpeg: {e}")
        raise
