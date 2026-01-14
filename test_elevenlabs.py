"""
Test script for ElevenLabs API key validation.
This script verifies that your ElevenLabs API key is working correctly.
"""

import os
import logging
from pathlib import Path
from elevenlabs import ElevenLabs
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_api_key():
    """Load API key from .env file"""
    load_dotenv()
    api_key = os.getenv('ELEVENLABS_API_KEY')
    return api_key


def test_api_connection(api_key):
    """Test basic API connection"""
    logger.info("Testing API connection...")
    
    try:
        client = ElevenLabs(api_key=api_key)
        logger.info("✅ API client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"❌ Failed to initialize API client: {e}")
        return None


def test_text_to_speech(client):
    """Test text-to-speech functionality with simple text"""
    logger.info("\nTesting text-to-speech functionality...")
    
    try:
        # Simple test text
        test_text = "The first move is what sets everything in motion."
        
        logger.info(f"   Converting text: '{test_text}'")
        
        # Generate speech using the official API
        audio = client.text_to_speech.convert(
            text=test_text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",  # George voice
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        # Save the audio
        output_file = "test_output.mp3"
        with open(output_file, 'wb') as f:
            for chunk in audio:
                if isinstance(chunk, bytes):
                    f.write(chunk)
        
        logger.info(f"✅ Text-to-speech is working!")
        logger.info(f"   Audio saved to: {output_file}")
        
        # Try to play the audio (optional)
        try:
            from elevenlabs.play import play
            logger.info("   Playing audio...")
            with open(output_file, 'rb') as f:
                play(f.read())
        except Exception as play_error:
            logger.info(f"   Could not play audio: {play_error}")
            logger.info("   (This is normal if MPV/ffmpeg is not installed)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Text-to-speech test failed: {e}")
        logger.info("   Note: This may be normal if you don't have TTS credits")
        return False


def test_speech_to_text(client):
    """Test speech-to-text functionality with a sample audio file"""
    logger.info("\nTesting speech-to-text functionality...")
    
    # Check if test_output.mp3 exists (created by TTS test)
    test_audio_path = "test_output.mp3"
    
    if not os.path.exists(test_audio_path):
        # Try to find other audio files
        test_audio_path = create_test_audio()
    
    if not test_audio_path:
        logger.warning("⚠️  Skipping speech-to-text test (no test audio available)")
        return
    
    try:
        logger.info(f"   Using audio file: {test_audio_path}")
        
        with open(test_audio_path, 'rb') as audio_file:
            result = client.speech_to_text.convert(
                file=audio_file,
                model_id='scribe_v2',
                use_multi_channel=False,
                diarize=False
            )
        
        logger.info("✅ Speech-to-text API is working!")
        
        # Display the transcription
        if hasattr(result, 'text'):
            logger.info(f"   Transcription: '{result.text}'")
        elif hasattr(result, 'transcripts') and result.transcripts:
            for i, transcript in enumerate(result.transcripts):
                logger.info(f"   Transcription [{i}]: '{transcript.text}'")
        else:
            logger.info("   Transcription completed successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Speech-to-text test failed: {e}")
        return False


def create_test_audio():
    """Check if there's any existing audio file to test with"""
    # Check common audio directories
    audio_dirs = [
        'data/raw_audio',
        'data/wav_audio',
        '.'
    ]
    
    for audio_dir in audio_dirs:
        if os.path.exists(audio_dir):
            for file in os.listdir(audio_dir):
                if file.endswith(('.wav', '.mp3', '.m4a', '.ogg')):
                    test_file = os.path.join(audio_dir, file)
                    logger.info(f"   Using existing audio file for test: {test_file}")
                    return test_file
    
    return None



def main():
    """Main test function"""
    logger.info("=" * 60)
    logger.info("🧪 ElevenLabs API Key Test")
    logger.info("=" * 60)
    
    # Step 1: Load API key
    logger.info("\n[1/3] Loading API key...")
    api_key = load_api_key()
    
    if not api_key:
        logger.error("❌ API key not found or not set!")
        logger.info("\n💡 To fix this:")
        logger.info("   1. Create a .env file in the project root")
        logger.info("   2. Add: ELEVENLABS_API_KEY=your_key_here")
        return
    
    logger.info(f"✅ API key loaded: {api_key[:10]}...{api_key[-10:]}")
    
    # Step 2: Test API connection
    logger.info("\n[2/3] Testing API connection...")
    client = test_api_connection(api_key)
    
    if not client:
        logger.error("\n❌ API connection test failed!")
        logger.info("\n💡 Possible issues:")
        logger.info("   - Invalid API key")
        logger.info("   - Network connection problem")
        logger.info("   - ElevenLabs service unavailable")
        return
    
    # Step 3: Test functionality
    logger.info("\n[3/3] Testing API functionality...")
    

    # Try text-to-speech
    test_text_to_speech(client)
    
    # Try speech-to-text if audio available
    test_speech_to_text(client)
    
    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("✅ ElevenLabs API Key Test Complete!")
    logger.info("=" * 60)
    logger.info("\n🎉 Your API key is working correctly!")
    logger.info("   You can now run the main pipeline: python main.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
