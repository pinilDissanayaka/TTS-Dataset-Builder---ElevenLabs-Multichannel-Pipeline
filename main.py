from utils import download_youtube_audio, split_audio_for_tts, transcribe_chunks, save_f5_metadata, load_urls_from_file

def main():
    # Load URLs from file
    urls = load_urls_from_file()
    
    if not urls:
        print("[!] No URLs found in urls.txt. Using default URL.")
        urls = ["https://www.youtube.com/shorts/Xk7IA4smUcw"]
    
    print(f"[+] Found {len(urls)} URL(s) to process\n")
    
    all_segments = []
    
    for idx, url in enumerate(urls, 1):
        print(f"\n{'='*60}")
        print(f"[+] Processing URL {idx}/{len(urls)}: {url}")
        print(f"{'='*60}\n")
        
        try:
            wav_file = download_youtube_audio(url)
            print(f"[+] Downloaded WAV: {wav_file}")

            wav_chunks = split_audio_for_tts(wav_file)
            print(f"[+] Created {len(wav_chunks)} chunks")

            segments = transcribe_chunks(wav_chunks)
            print(f"[+] Transcribed {len(segments)} chunks")
            
            all_segments.extend(segments)
            
        except Exception as e:
            print(f"[!] Error processing {url}: {str(e)}")
            continue
    
    if all_segments:
        save_f5_metadata(all_segments)
        print(f"\n[+] Pipeline complete! Processed {len(all_segments)} total chunks.")
        print("[+] Ready for F5-TTS training.")
    else:
        print("[!] No segments were successfully processed.")

if __name__ == "__main__":
    main()
