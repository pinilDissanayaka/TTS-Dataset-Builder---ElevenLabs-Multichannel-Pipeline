import subprocess
import os
import logging
from config import RAW_AUDIO_DIR

logger = logging.getLogger(__name__)


def download_podcast(youtube_url: str):
    """
    Download audio from YouTube URL or playlist.
    Downloads as WAV format for best quality.
    """
    os.makedirs(RAW_AUDIO_DIR, exist_ok=True)

    logger.info(f"Downloading audio from: {youtube_url}")

    cmd = [
        "yt-dlp",
        "-x",  # Extract audio
        "--audio-format", "wav",  # Convert to WAV
        "--audio-quality", "0",  # Best quality
        "--yes-playlist",  # Download playlists
        "-o", f"{RAW_AUDIO_DIR}/%(title)s.%(ext)s",  # Output template
        youtube_url
    ]

    try:
        subprocess.run(cmd, check=True)
        logger.info("✓ Download completed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Download failed: {e}")
        raise
