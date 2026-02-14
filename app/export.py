#   export.py

from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
from moviepy.audio.fx import AudioLoop
import os

def finalize_video():
    if not os.path.exists("final_upload"):
        os.makedirs("final_upload")

    music_path = "background/in-the-morning-the-grey-room-clark-sims.mp3"
    video_path = "media/videos/stunning_v6/1080p60/UltimateUniversalRace.mp4"

    # 1. Verify file exists before starting
    if not os.path.exists(music_path):
        print(f"❌ ERROR: Music file not found at {music_path}")
        return

    video = VideoFileClip(video_path)
    bg_music = AudioFileClip(music_path)
    
    print(f"Video duration: {video.duration}s | Music duration: {bg_music.duration}s")

    # 2. Advanced Looping Logic
    if bg_music.duration < video.duration:
        print("Looping background music...")
        bg_music = bg_music.with_effects([AudioLoop(duration=video.duration)])
    else:
        bg_music = bg_music.with_duration(video.duration)

    # 3. Boost volume slightly for testing (Changed from 0.3 to 0.5)
    bg_music = bg_music.with_volume_scaled(0.5)

    audio_tracks = [bg_music]
    if video.audio is not None:
        print(f"✅ Thuds detected (Duration: {video.audio.duration}s). Mixing...")
        audio_tracks.append(video.audio)
    else:
        print("⚠️ No thuds found in Manim video.")

    final_audio = CompositeAudioClip(audio_tracks)

    # 4. FORCE RESAMPLING
    # Setting fps=44100 inside write_videofile is the 'magic' fix for missing audio
    final_v = video.with_audio(final_audio)
    
    print("Writing final file...")
    final_v.write_videofile(
        "final_upload/test.mp4", 
        fps=60, 
        codec="libx264", 
        audio_codec="aac",
        audio_fps=44100,  # <--- THIS IS THE KEY FIX
        temp_audiofile='temp-audio.m4a', 
        remove_temp=True
    )
    print("✨ Final video saved to final_upload/test.mp4")

if __name__ == "__main__":
    finalize_video()