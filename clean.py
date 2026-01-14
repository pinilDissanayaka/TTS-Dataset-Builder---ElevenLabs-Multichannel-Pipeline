import os
import pandas as pd
from langdetect import detect, LangDetectException
from config import METADATA_CSV, WAV_DIR

def is_sinhala_text(text):
    """
    Check if the text is in Sinhala language using langdetect.
    Returns True if detected language is Sinhala ('si'), False otherwise.
    """
    if not text or not text.strip():
        return False
    
    try:
        detected_lang = detect(text)
        return detected_lang == 'si'
    except LangDetectException:
        # If detection fails (e.g., too short text, only punctuation)
        # Fall back to Unicode range check
        return is_sinhala_by_unicode(text)

def is_sinhala_by_unicode(text):
    """
    Fallback method: Check if text contains Sinhala characters by Unicode range.
    Sinhala Unicode range: U+0D80 to U+0DFF
    """
    if not text or not text.strip():
        return False
    
    sinhala_chars = 0
    total_chars = 0
    
    for char in text:
        # Skip whitespace and punctuation
        if char in ' \t\n.,!?;:\'"()[]{}…-–—' or char.isdigit():
            continue
        
        total_chars += 1
        code_point = ord(char)
        
        # Sinhala Unicode block: 0D80–0DFF
        if 0x0D80 <= code_point <= 0x0DFF:
            sinhala_chars += 1
    
    # If at least 80% of characters are Sinhala, consider it Sinhala text
    if total_chars == 0:
        return False
    
    return (sinhala_chars / total_chars) >= 0.8

def clean_non_sinhala_rows(metadata_csv=METADATA_CSV, wav_dir=WAV_DIR, dry_run=False):
    """
    Clean the dataset by removing rows that contain non-Sinhala characters.
    Also deletes the corresponding audio files.
    
    Args:
        metadata_csv: Path to the metadata CSV file
        wav_dir: Directory containing the audio files
        dry_run: If True, only show what would be deleted without actually deleting
    
    Returns:
        Dictionary with statistics about the cleaning process
    """
    if not os.path.exists(metadata_csv):
        print(f"[!] Metadata file not found: {metadata_csv}")
        return {"error": "Metadata file not found"}
    
    print(f"[+] Loading metadata from: {metadata_csv}")
    
    # Read the metadata file
    rows_to_keep = []
    rows_to_delete = []
    
    with open(metadata_csv, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"[+] Total rows: {len(lines)}")
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Parse the line (format: filename|text)
        parts = line.split('|', 1)
        if len(parts) != 2:
            print(f"[!] Skipping malformed line: {line}")
            continue
        
        filename, text = parts
        
        # Check if text is in Sinhala language
        if is_sinhala_text(text):
            rows_to_keep.append(line)
        else:
            rows_to_delete.append((filename, text))
            try:
                detected_lang = detect(text)
                print(f"[!] Non-Sinhala text found (detected: {detected_lang}): {filename} -> {text}")
            except:
                print(f"[!] Non-Sinhala text found: {filename} -> {text}")
    
    print(f"\n[+] Rows to keep: {len(rows_to_keep)}")
    print(f"[!] Rows to delete: {len(rows_to_delete)}")
    
    if dry_run:
        print("\n[DRY RUN] - No files will be deleted")
        for filename, text in rows_to_delete:
            print(f"  Would delete: {filename}")
        return {
            "total_rows": len(lines),
            "kept": len(rows_to_keep),
            "deleted": len(rows_to_delete),
            "dry_run": True
        }
    
    # Delete audio files
    deleted_files = 0
    for filename, text in rows_to_delete:
        audio_path = os.path.join(wav_dir, filename)
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
                deleted_files += 1
                print(f"[+] Deleted audio file: {audio_path}")
            except Exception as e:
                print(f"[!] Error deleting {audio_path}: {e}")
        else:
            print(f"[!] Audio file not found: {audio_path}")
    
    # Save cleaned metadata
    if rows_to_keep:
        with open(metadata_csv, 'w', encoding='utf-8') as f:
            for row in rows_to_keep:
                f.write(row + '\n')
        print(f"\n[+] Saved cleaned metadata to: {metadata_csv}")
    else:
        print(f"\n[!] No rows to keep! Metadata file not modified.")
    
    stats = {
        "total_rows": len(lines),
        "kept": len(rows_to_keep),
        "deleted": len(rows_to_delete),
        "deleted_audio_files": deleted_files,
        "dry_run": False
    }
    
    print(f"\n{'='*60}")
    print("[+] Cleaning complete!")
    print(f"  Total rows processed: {stats['total_rows']}")
    print(f"  Rows kept: {stats['kept']}")
    print(f"  Rows deleted: {stats['deleted']}")
    print(f"  Audio files deleted: {stats['deleted_audio_files']}")
    print(f"{'='*60}")
    
    return stats

if __name__ == "__main__":
    # Run the cleaning process
    print("Starting data cleaning process...\n")
    
    # First do a dry run to see what would be deleted
    print("=== DRY RUN ===")
    clean_non_sinhala_rows(dry_run=True)
    
    # Ask for confirmation
    response = input("\nDo you want to proceed with deletion? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        print("\n=== ACTUAL CLEANING ===")
        clean_non_sinhala_rows(dry_run=False)
    else:
        print("[!] Cleaning cancelled.")