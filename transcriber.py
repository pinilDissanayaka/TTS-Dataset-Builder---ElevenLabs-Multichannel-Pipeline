import os
import logging
from elevenlabs import ElevenLabs
from pydub import AudioSegment
from config import (
    WAV_AUDIO_DIR,
    ELEVENLABS_API_KEY,
    ELEVENLABS_MODEL,
    USE_MULTI_CHANNEL,
    CHUNK_DURATION_SEC
)

logger = logging.getLogger(__name__)


def transcribe_audio():
    """
    Transcribe audio files using ElevenLabs multichannel speech-to-text.
    Returns a dictionary with transcripts organized by file.
    """
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    results = {}

    for file in os.listdir(WAV_AUDIO_DIR):
        if not file.endswith(".wav"):
            continue

        file_path = os.path.join(WAV_AUDIO_DIR, file)
        logger.info(f"Transcribing: {file}")

        # Get file info
        audio = AudioSegment.from_file(file_path)
        duration_sec = len(audio) / 1000.0
        num_channels = audio.channels

        # Process large files in chunks
        if duration_sec > CHUNK_DURATION_SEC:
            logger.info(f"  Large file detected ({duration_sec:.1f}s), processing in chunks...")
            all_transcripts = process_large_multichannel_file(
                client, file_path, CHUNK_DURATION_SEC
            )
            results[file] = convert_transcripts_to_segments(all_transcripts)
        else:
            # Process normally
            with open(file_path, 'rb') as audio_file:
                result = client.speech_to_text.convert(
                    file=audio_file,
                    model_id=ELEVENLABS_MODEL,
                    use_multi_channel=USE_MULTI_CHANNEL,
                    diarize=False,
                    timestamps_granularity='word'
                )

            results[file] = convert_transcripts_to_segments(
                result.transcripts if hasattr(result, 'transcripts') else [result]
            )

        logger.info(f"  ✓ Completed: {len(results[file])} segments")

    return results


def process_large_multichannel_file(client, file_path, chunk_duration):
    """Process large multichannel files in chunks"""
    audio = AudioSegment.from_file(file_path)
    duration_ms = len(audio)
    chunk_size_ms = chunk_duration * 1000
    all_transcripts = []

    for start_ms in range(0, duration_ms, chunk_size_ms):
        end_ms = min(start_ms + chunk_size_ms, duration_ms)

        # Extract chunk
        chunk = audio[start_ms:end_ms]
        chunk_file = f"temp_chunk_{start_ms}.wav"
        chunk.export(chunk_file, format="wav")

        # Transcribe chunk
        with open(chunk_file, 'rb') as audio_file:
            result = client.speech_to_text.convert(
                file=audio_file,
                model_id=ELEVENLABS_MODEL,
                use_multi_channel=USE_MULTI_CHANNEL,
                diarize=False,
                timestamps_granularity='word'
            )

        # Adjust timestamps
        if hasattr(result, 'transcripts'):
            for transcript in result.transcripts:
                for word in transcript.words or []:
                    word.start += start_ms / 1000
                    word.end += start_ms / 1000
            all_transcripts.extend(result.transcripts)

        # Clean up
        os.remove(chunk_file)

    return all_transcripts


def convert_transcripts_to_segments(transcripts):
    """
    Convert ElevenLabs multichannel transcripts to segment format.
    Combines all channels and creates a time-ordered conversation.
    """
    all_words = []

    # Handle both multichannel and single-channel responses
    if isinstance(transcripts, list):
        for transcript in transcripts:
            if hasattr(transcript, 'words') and transcript.words:
                for word in transcript.words:
                    if word.type == 'word':
                        all_words.append({
                            'text': word.text,
                            'start': word.start,
                            'end': word.end,
                            'speaker_id': getattr(word, 'speaker_id', 'speaker_0'),
                            'channel': getattr(transcript, 'channel_index', 0)
                        })
            elif hasattr(transcript, 'text'):
                # Fallback for single-channel response
                all_words.append({
                    'text': transcript.text,
                    'start': 0,
                    'end': 0,
                    'speaker_id': 'speaker_0',
                    'channel': 0
                })

    # Sort by timestamp
    all_words.sort(key=lambda w: w['start'])

    # Group consecutive words by speaker into segments
    segments = []
    current_speaker = None
    current_words = []
    start_time = 0

    for word in all_words:
        if word['speaker_id'] != current_speaker:
            # Save previous segment
            if current_words:
                segments.append({
                    'start': start_time,
                    'end': current_words[-1]['end'],
                    'text': ' '.join([w['text'] for w in current_words]),
                    'speaker': current_speaker
                })

            # Start new segment
            current_speaker = word['speaker_id']
            current_words = [word]
            start_time = word['start']
        else:
            current_words.append(word)

    # Add the last segment
    if current_words:
        segments.append({
            'start': start_time,
            'end': current_words[-1]['end'],
            'text': ' '.join([w['text'] for w in current_words]),
            'speaker': current_speaker
        })

    return segments


def create_conversation_transcript(result):
    """
    Create a conversation-style transcript with speaker labels.
    Useful for viewing the transcription results.
    """
    conversation = []

    if hasattr(result, 'transcripts'):
        all_words = []

        # Collect all words from all channels
        for transcript in result.transcripts:
            for word in transcript.words or []:
                if word.type == 'word':
                    all_words.append({
                        'text': word.text,
                        'start': word.start,
                        'speaker_id': word.speaker_id,
                        'channel': transcript.channel_index
                    })

        # Sort by timestamp
        all_words.sort(key=lambda w: w['start'])

        # Group consecutive words by speaker
        current_speaker = None
        current_text = []

        for word in all_words:
            if word['speaker_id'] != current_speaker:
                if current_text:
                    conversation.append({
                        'speaker': current_speaker,
                        'text': ' '.join(current_text)
                    })
                current_speaker = word['speaker_id']
                current_text = [word['text']]
            else:
                current_text.append(word['text'])

        # Add the last segment
        if current_text:
            conversation.append({
                'speaker': current_speaker,
                'text': ' '.join(current_text)
            })

    return conversation
