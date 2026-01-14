# ElevenLabs API Configuration
ELEVENLABS_API_KEY = "YOUR_API_KEY"  # Replace with your ElevenLabs API key

# Audio Settings
SAMPLE_RATE = 16000  # 16kHz recommended for ElevenLabs
CHANNELS = 1  # Will be converted from multichannel after transcription

# Chunking Settings
MIN_SEGMENT_SEC = 2.0
MAX_SEGMENT_SEC = 10.0
CHUNK_DURATION_SEC = 300  # 5-minute chunks for large files

# Language
LANGUAGE = "si"  # Sinhala

# Directory Structure
RAW_AUDIO_DIR = "data/raw_audio"
WAV_AUDIO_DIR = "data/wav_audio"
CHUNKS_WAV_DIR = "data/chunks/wavs"
FINAL_WAVS_DIR = "data/final_dataset/wavs"
METADATA_PATH = "data/final_dataset/metadata.csv"

# ElevenLabs Speech-to-Text Settings
ELEVENLABS_MODEL = "scribe_v2"
USE_MULTI_CHANNEL = True
MAX_CHANNELS = 5