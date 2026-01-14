import os
from dotenv import load_dotenv

load_dotenv()

# ElevenLabs
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_MODEL = "scribe_v2"
USE_MULTI_CHANNEL = False

# Audio processing
CHUNK_MIN_SEC = 3      # Minimum chunk length
CHUNK_MAX_SEC = 10     # Maximum chunk length
MIN_SILENCE_LEN_MS = 400
SILENCE_THRESH_DB = -35
KEEP_SILENCE_MS = 150

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
WAV_DIR = os.path.join(BASE_DIR, "wavs")
METADATA_CSV = os.path.join(BASE_DIR, "metadata.csv")
URLs_FILE = os.path.join(BASE_DIR, "urls.txt")
