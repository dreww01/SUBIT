
import os
import subprocess
from faster_whisper import WhisperModel
from datetime import datetime
import time

# ------------------- CONFIGURATION -------------------

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

VIDEO_DIR = "videos"
AUDIO_DIR = "audio"
OUTPUT_DIR = "outputs"
ASS_DIR = "subtitles"
FONTS_DIR = "fonts"

# Create folders if they don't exist
for folder in [VIDEO_DIR, AUDIO_DIR, OUTPUT_DIR, ASS_DIR, FONTS_DIR]:
    os.makedirs(folder, exist_ok=True)


# List all video files and let user select if more than one
video_files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith((".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv"))]
if not video_files:
    raise FileNotFoundError(f"No video file found in {VIDEO_DIR}/ folder.")
elif len(video_files) == 1:
    VIDEO_PATH = os.path.join(VIDEO_DIR, video_files[0])
else:
    print("Multiple video files found:")
    for idx, fname in enumerate(video_files, 1):
        print(f"  {idx}: {fname}")
    while True:
        try:
            choice = int(input(f"Select video file [1-{len(video_files)}]: "))
            if 1 <= choice <= len(video_files):
                VIDEO_PATH = os.path.join(VIDEO_DIR, video_files[choice-1])
                break
            else:
                print("Invalid selection. Try again.")
        except ValueError:
            print("Please enter a number.")

# Paths
AUDIO_PATH = os.path.join(AUDIO_DIR, f"audio_{timestamp}.wav")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"output_with_sub_{timestamp}.mp4")
ASS_PATH = os.path.join(ASS_DIR, f"subtitles_{timestamp}.ass")
CUSTOM_FONT_NAME = "Playfair Display"

# ------------------- USER INPUTS -------------------

COLOR_MAP = {
    "black": "#000000", "white": "#FFFFFF", "red": "#FF0000", "green": "#00FF00",
    "blue": "#0000FF", "yellow": "#FFFF00", "cyan": "#00FFFF", "magenta": "#FF00FF",
    "orange": "#FFA500", "purple": "#800080"
}

def ask(prompt, default=None, cast=str):
    value = input(f"{prompt} [{default}]: ") or str(default)
    try:
        return cast(value)
    except (ValueError, TypeError):
        print(f"⚠️ Invalid input. Using default: {default}")
        return default

def get_user_inputs():
    max_words_per_line = ask("Words per line", 6, int)
    color_input = ask("Color (Hex or name)", "white", str).lower()
    subtitle_color = COLOR_MAP.get(color_input, color_input)
    font_weight = ask("Font thickness (100–900)", 400, int)
    font_size = ask("Font size", 48, int)
    shadow_strength = ask("Shadow strength (0=None, 1=Normal, 3=Thick)", 1.0, float)
    enable_bounce = ask("Bounce effect? (True/False)", "False", str).lower() == "true"
    lang = ask("Language ('th','en','ja','zh')", "en", str).lower()
    print("\nSubtitle position:\n1 = Bottom\n2 = Middle\n3 = Top\n4 = Slightly above bottom")
    position_choice = ask("Choose position", 1, str)
    alignment_map = {"1": 2, "2": 5, "3": 8, "4": 5}
    alignment = alignment_map.get(position_choice, 2)
    margin_v = 180 if position_choice == "4" else 30

    return {
        "video_path": VIDEO_PATH,
        "audio_path": AUDIO_PATH,
        "output_path": OUTPUT_PATH,
        "max_words_per_line": max_words_per_line,
        "subtitle_color": subtitle_color,
        "font_weight": font_weight,
        "font_size": font_size,
        "shadow_strength": shadow_strength,
        "enable_bounce": enable_bounce,
        "lang": lang,
        "alignment": alignment,
        "margin_v": margin_v,
    }

# ------------------- CORE FUNCTIONS -------------------

# function to calculate processing speed
def print_speed(file_path, elapsed, label):
    """Prints the processing speed in MB/s for a given file and elapsed time."""
    if os.path.isfile(file_path):
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        speed = size_mb / elapsed if elapsed > 0 else 0
        print(f"⚠ ⚠ {label} speed: {speed:.2f} MB/s ({size_mb:.2f} MB in {elapsed:.2f} s) \n this code was written by github.com/dreww01")

#  function to extract audio
def extract_audio(video_path, audio_path):
    try:
        start = time.time()
        subprocess.run([
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2",
            audio_path
        ], check=True)
        elapsed = time.time() - start
        print_speed(audio_path, elapsed, "Audio extraction")
    except subprocess.CalledProcessError:
        print("❌ Failed to extract audio.")
        exit(1)

#  function to format time
def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int((seconds - int(seconds)) * 100)
    return f"{hours}:{minutes:02}:{secs:02}.{centis:02}"

# function to create subtitle file
def create_ass_file(segments, settings):
    hex_color = settings["subtitle_color"].lstrip("#")
    bgr_hex = f"&H00{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"
    try:
        with open(ASS_PATH, "w", encoding="utf-8") as f:
            # Header
            f.write("[Script Info]\nScriptType: v4.00+\nPlayResX:1280\nPlayResY:720\nWrapStyle:0\nScaledBorderAndShadow:yes\n\n")
            # Styles
            f.write("[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n")
            f.write(f"Style: Default,{CUSTOM_FONT_NAME},{settings['font_size']},{bgr_hex},{settings['font_weight']},0,0,0,100,100,0,0,1,2,{settings['shadow_strength']},{settings['alignment']},10,10,{settings['margin_v']},1\n\n")
            # Events
            f.write("[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n")
            for segment in segments:
                words = segment.text.strip().split()
                if not words:
                    continue
                duration = segment.end - segment.start
                avg_word_duration = duration / len(words)
                for i in range(0, len(words), settings["max_words_per_line"]):
                    chunk = words[i:i + settings["max_words_per_line"]]
                    chunk_start = segment.start + i * avg_word_duration
                    chunk_end = chunk_start + len(chunk) * avg_word_duration
                    text = " ".join(chunk)
                    if settings["enable_bounce"]:
                        effect = r"{\fscx30\fscy30\t(0,75,\fscx115\fscy115)\t(75,150,\fscx100\fscy100)}"
                        text = f"{effect}{text}"
                    f.write(f"Dialogue: 0,{format_time(chunk_start)},{format_time(chunk_end)},Default,,0,0,0,,{text}\n")
    except OSError:
        print("❌ Failed to create .ass subtitle file.")
        exit(1)

# function to burn subtitles
def burn_subtitles(video_path, ass_path, output_path):
    if not os.path.isfile(ass_path):
        print(f"❌ Subtitle file not found: {ass_path}")
        exit(1)
    # Convert paths to forward slashes for ffmpeg compatibility
    ass_path_ffmpeg = ass_path.replace("\\", "/")
    fonts_dir_ffmpeg = FONTS_DIR.replace("\\", "/")
    try:
        start = time.time()
        subprocess.run([
            "ffmpeg", "-y", "-i", video_path,
            "-vf", f"ass={ass_path_ffmpeg}:fontsdir={fonts_dir_ffmpeg}",
            output_path
        ], check=True)
        elapsed = time.time() - start
        print_speed(output_path, elapsed, "Subtitle burning")
    except subprocess.CalledProcessError:
        print("❌ Failed to burn subtitles into video.")
        exit(1)

# ------------------- MAIN -------------------

def main():
    settings = get_user_inputs()
    print("🎬 Extracting audio...")
    extract_audio(settings["video_path"], settings["audio_path"])

    print("🧠 Running speech-to-text...")
    model = WhisperModel("small", compute_type="int8")
    segments, _ = model.transcribe(settings["audio_path"], language=settings["lang"])

    print("📝 Creating subtitle file...")
    create_ass_file(segments, settings)

    print("🔥 Burning subtitles into video...")
    burn_subtitles(settings["video_path"], ASS_PATH, settings["output_path"])

    print(f"✅ Done! Output saved to {settings['output_path']}")

if __name__ == "__main__":
    main()
