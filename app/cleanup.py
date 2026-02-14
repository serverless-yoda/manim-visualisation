import os
import shutil

def cleanup_project():
    # Folders to target
    manim_media = "media"
    temp_audio = "temp-audio.m4a"
    
    print("🧹 Starting cleanup...")

    # 1. Remove the entire Manim media folder (caches and raw renders)
    if os.path.exists(manim_media):
        try:
            shutil.rmtree(manim_media)
            print(f"✅ Deleted {manim_media} folder (cache cleared).")
        except Exception as e:
            print(f"⚠️ Could not delete media folder: {e}")

    # 2. Remove temporary audio files from MoviePy
    if os.path.exists(temp_audio):
        os.remove(temp_audio)
        print("✅ Deleted temporary audio file.")

    print("🚀 Project is clean! Only your data, assets, and final_upload remain.")

if __name__ == "__main__":
    confirm = input("This will delete all Manim caches and raw videos. Continue? (y/n): ")
    if confirm.lower() == 'y':
        cleanup_project()