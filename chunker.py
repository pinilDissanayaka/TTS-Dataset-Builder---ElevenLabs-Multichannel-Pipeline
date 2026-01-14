import os
from pydub import AudioSegment
from config import (
    WAV_AUDIO_DIR,
    CHUNKS_WAV_DIR,
    MIN_SEGMENT_SEC,
    MAX_SEGMENT_SEC
)

def chunk_with_timestamps(transcripts):
    os.makedirs(CHUNKS_WAV_DIR, exist_ok=True)
    chunk_data = []

    for file, segments in transcripts.items():
        audio = AudioSegment.from_wav(os.path.join(WAV_AUDIO_DIR, file))
        base = os.path.splitext(file)[0]

        for i, seg in enumerate(segments):
            duration = seg["end"] - seg["start"]
            if duration < MIN_SEGMENT_SEC or duration > MAX_SEGMENT_SEC:
                continue

            start_ms = int(seg["start"] * 1000)
            end_ms = int(seg["end"] * 1000)

            chunk = audio[start_ms:end_ms]
            name = f"{base}_{i}.wav"
            chunk.export(os.path.join(CHUNKS_WAV_DIR, name), format="wav")

            chunk_data.append((name, seg["text"]))

    return chunk_data
