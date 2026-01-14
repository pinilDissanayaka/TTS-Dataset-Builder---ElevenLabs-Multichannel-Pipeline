import os
from pydub import AudioSegment, silence
import yt_dlp
from elevenlabs import ElevenLabs
from config import *

def download_youtube_audio(url):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'postprocessor_args': ['-ar', '24000', '-ac', '1'],  # 24kHz mono
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")

def split_audio_for_tts(input_wav, output_dir=WAV_DIR):
    os.makedirs(output_dir, exist_ok=True)
    audio = AudioSegment.from_wav(input_wav)

    chunks = silence.split_on_silence(
        audio,
        min_silence_len=MIN_SILENCE_LEN_MS,
        silence_thresh=SILENCE_THRESH_DB,
        keep_silence=KEEP_SILENCE_MS
    )

    out_files = []
    for i, chunk in enumerate(chunks):
        if len(chunk) < CHUNK_MIN_SEC*1000 or len(chunk) > CHUNK_MAX_SEC*1000:
            continue
        path = os.path.join(output_dir, f"chunk_{i:04d}.wav")
        chunk.export(path, format="wav")
        out_files.append(path)

    return out_files

def transcribe_chunks(wav_files):
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    segments_all = []

    for i, file_path in enumerate(wav_files):
        print(f"[+] Transcribing {file_path} ...")
        with open(file_path, 'rb') as audio_file:
            result = client.speech_to_text.convert(
                file=audio_file,
                model_id=ELEVENLABS_MODEL,
                use_multi_channel=USE_MULTI_CHANNEL,
                diarize=False,
                timestamps_granularity='word'
            )

        # Simple fallback: use result.text if word-level missing
        text = getattr(result, "text", None)
        if not text and hasattr(result, "transcripts"):
            words = []
            for t in result.transcripts:
                for w in getattr(t, "words", []):
                    if getattr(w, "type", "") == "word":
                        words.append(w.text)
            text = " ".join(words)

        if not text:
            text = "silence"

        segments_all.append({"file": os.path.basename(file_path), "text": text.strip()})

    return segments_all

def save_f5_metadata(segments, metadata_csv=METADATA_CSV):
    with open(metadata_csv, "w", encoding="utf-8") as f:
        for seg in segments:
            f.write(f"{seg['file']}|{seg['text']}\n")
    print(f"[+] Saved metadata to {metadata_csv}")

def load_urls_from_file(file_path=URLs_FILE):
    """Load URLs from a text file, one URL per line. Skips empty lines and comments."""
    if not os.path.exists(file_path):
        print(f"[!] URLs file not found: {file_path}")
        return []
    
    urls = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments (lines starting with #)
            if line and not line.startswith('#'):
                urls.append(line)
    
    return urls
