import os
import shutil
from config import FINAL_WAVS_DIR, METADATA_PATH

def build_dataset(chunk_data):
    os.makedirs(FINAL_WAVS_DIR, exist_ok=True)

    with open(METADATA_PATH, "w", encoding="utf-8") as meta:
        for idx, (chunk_file, text) in enumerate(chunk_data, start=1):
            new_name = f"{idx:05d}.wav"
            shutil.copy(
                f"data/chunks/wavs/{chunk_file}",
                f"{FINAL_WAVS_DIR}/{new_name}"
            )
            meta.write(f"{idx:05d}|{text}\n")
