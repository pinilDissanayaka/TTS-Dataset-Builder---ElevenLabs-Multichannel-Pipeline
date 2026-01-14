import os
import logging
from pydub import AudioSegment
from config import RAW_AUDIO_DIR, WAV_AUDIO_DIR, SAMPLE_RATE, CHANNELS

logger = logging.getLogger(__name__)


def normalize_audio():
    """
    Normalize audio files to optimal settings for ElevenLabs:
    - 16kHz sample rate (recommended by ElevenLabs)
    - Convert to mono for final processing
    - Export as WAV format
    """
    os.makedirs(WAV_AUDIO_DIR, exist_ok=True)

    for file in os.listdir(RAW_AUDIO_DIR):
        if not file.endswith(".wav"):
            continue

        logger.info(f"  Normalizing: {file}")
        audio = AudioSegment.from_wav(os.path.join(RAW_AUDIO_DIR, file))

        # Set to 16kHz for optimal ElevenLabs performance
        audio = audio.set_frame_rate(SAMPLE_RATE)

        # Keep original channels for multichannel transcription
        # (Will be converted to mono later if needed)
        output_path = os.path.join(WAV_AUDIO_DIR, file)
        audio.export(output_path, format="wav")

        logger.info(f"  ✓ Normalized: {file} ({audio.channels} channels, {SAMPLE_RATE}Hz)")
