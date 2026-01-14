import logging
from downloader import download_podcast
from audio_processing import normalize_audio
from transcriber import transcribe_audio
from chunker import chunk_with_timestamps
from dataset_builder import build_dataset

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dataset_builder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_youtube_urls(file_path='youtube_urls.txt'):
    """
    Load YouTube URLs from a text file.
    Skips empty lines and comments (lines starting with #).
    
    Args:
        file_path: Path to the file containing YouTube URLs
        
    Returns:
        List of YouTube URLs
    """
    urls = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    urls.append(line)
        
        if not urls:
            logger.warning(f"No URLs found in {file_path}")
        else:
            logger.info(f"Loaded {len(urls)} URL(s) from {file_path}")
        
        return urls
    except FileNotFoundError:
        logger.error(f"URL file not found: {file_path}")
        logger.info("Please create 'youtube_urls.txt' and add YouTube URLs (one per line)")
        raise


def main():
    """
    Main pipeline for building a TTS dataset from YouTube audio.

    Pipeline steps:
    1. Download YouTube audio file (supports playlists)
    2. Normalize audio to 16kHz for optimal ElevenLabs processing
    3. Transcribe using ElevenLabs multichannel speech-to-text
    4. Chunk audio based on transcription timestamps
    5. Build final dataset with metadata
    """

    logger.info("=" * 60)
    logger.info("🎙️  TTS Dataset Builder - ElevenLabs Multichannel Pipeline")
    logger.info("=" * 60)

    # Load YouTube URLs from file
    youtube_urls = load_youtube_urls('youtube_urls.txt')
    
    # Step 1: Download audio from YouTube
    logger.info("\n[1/5] Downloading YouTube audio...")
    for url in youtube_urls:
        download_podcast(url)

    # Step 2: Normalize audio (convert to 16kHz for ElevenLabs)
    logger.info("\n[2/5] Normalizing audio...")
    normalize_audio()

    # Step 3: Transcribe with ElevenLabs multichannel
    logger.info("\n[3/5] Transcribing with ElevenLabs...")
    transcripts = transcribe_audio()

    # Step 4: Chunk audio based on timestamps
    logger.info("\n[4/5] Chunking audio with timestamps...")
    chunk_data = chunk_with_timestamps(transcripts)

    # Step 5: Build final dataset
    logger.info("\n[5/5] Building final dataset...")
    build_dataset(chunk_data)

    logger.info("\n" + "=" * 60)
    logger.info("✅ TTS dataset ready!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
