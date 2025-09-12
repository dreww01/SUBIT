import os
import subprocess
from faster_whisper import WhisperModel
import pysrt
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except NameError:
    # __file__ is not defined in interactive mode
    pass
# ------------------- CONFIGURATION -------------------
# the video path 
print("Current working directory:", os.getcwd())

VIDEO_DIR = "videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

# Auto-detect the first video file in /videos
VIDEO_PATH = None
for file in os.listdir(VIDEO_DIR):
    if file.lower().endswith((".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv")):
        VIDEO_PATH = os.path.join(VIDEO_DIR, file)
        break

if not VIDEO_PATH:
    raise FileNotFoundError(f"No video file found in {VIDEO_DIR}/ folder.")

# the audio path
AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# the subtitle path
FONTS_DIR = "fonts"
os.makedirs(FONTS_DIR, exist_ok=True)


ASS_PATH = f"subtitles_{timestamp}.ass"
MODEL_SIZE = "small"
CUSTOM_FONT_NAME = "Playfair Display"
CUSTOM_FONT_PATH = os.path.join(FONTS_DIR, "PlayfairDisplay-VariableFont_wght.ttf")



def ask(prompt, default=None, cast=str):
    """Ask user for input with default value and safe type conversion."""
    value = input(f"{prompt} [{default}]: ") or str(default)
    try:
        return cast(value)
    except (ValueError, TypeError):
        print(f"⚠️ Invalid input. Using default: {default}")
        return default


def get_user_inputs():
    """Collect subtitle styling and position settings from user input with defaults."""
    
    video_path = VIDEO_PATH


    # auto-generate unique names for audio and output
    audio_path = os.path.join(AUDIO_DIR, f"audio_{timestamp}.wav")
    output_path = f"output_with_sub_{timestamp}.mp4"

    max_words_per_line = ask("Words per line", 6, int)
    subtitle_color = ask("Color (Hex)", "#FFFF00", str)
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
        "video_path": video_path,
        "audio_path": audio_path,
        "output_path": output_path,
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


def extract_audio(video_path, audio_path):
    """Extract audio from video using ffmpeg."""
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2",
            audio_path
        ], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to extract audio.")
        exit(1)


def format_time(seconds):
    """Formats seconds into ASS subtitle timestamp format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int((seconds - int(seconds)) * 100)
    return f"{hours}:{minutes:02}:{secs:02}.{centis:02}"


def parse_srt_to_segments(srt_path):
    """Parse .srt file into segment-like objects using pysrt."""
    subs = pysrt.open(srt_path, encoding="utf-8")
    segments = []
    for sub in subs:
        start = sub.start.ordinal / 1000.0
        end = sub.end.ordinal / 1000.0
        text = sub.text.replace("\n", " ")
        segments.append(type("Segment", (object,), {"start": start, "end": end, "text": text}))
    return segments


def create_ass_file(segments, settings):
    """Creates an .ass subtitle file from transcription or parsed segments."""
    hex_color = settings["subtitle_color"].lstrip("#")
    bgr_hex = f"&H00{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"

    try:
        with open(ASS_PATH, "w", encoding="utf-8") as f:
            # Header
            f.write("[Script Info]\n"
                    "ScriptType: v4.00+\n"
                    "PlayResX: 1280\n"
                    "PlayResY: 720\n"
                    "WrapStyle: 0\n"
                    "ScaledBorderAndShadow: yes\n"
                    "YCbCr Matrix: TV.601\n\n")

            # Styles
            f.write("[V4+ Styles]\n"
                    "Format: Name, Fontname, Fontsize, PrimaryColour, Bold, Italic, "
                    "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, "
                    "Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")

            f.write(f"Style: Default,{CUSTOM_FONT_NAME},{settings['font_size']},{bgr_hex},"
                    f"{settings['font_weight']},0,0,0,100,100,0,0,1,2,"
                    f"{settings['shadow_strength']},{settings['alignment']},10,10,"
                    f"{settings['margin_v']},1\n\n")

            # Events
            f.write("[Events]\n"
                    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, "
                    "MarginV, Effect, Text\n")

            for segment in segments:
                words = segment.text.strip().split()
                total_words = len(words)
                if total_words == 0:
                    continue

                duration = segment.end - segment.start
                avg_word_duration = duration / total_words

                for i in range(0, total_words, settings["max_words_per_line"]):
                    chunk_words = words[i:i + settings["max_words_per_line"]]
                    chunk_start = segment.start + i * avg_word_duration
                    chunk_end = chunk_start + len(chunk_words) * avg_word_duration

                    text = " ".join(chunk_words)
                    if settings["enable_bounce"]:
                        effect = r"{\fscx30\fscy30\t(0,75,\fscx115\fscy115)\t(75,150,\fscx100\fscy100)}"
                        text = f"{effect}{text}"

                    f.write(f"Dialogue: 0,{format_time(chunk_start)},"
                            f"{format_time(chunk_end)},Default,,0,0,0,,{text}\n")
    except OSError:
        print("❌ Failed to create .ass subtitle file.")
        exit(1)


def burn_subtitles(video_path, ass_path, output_path):
    """Burns subtitles into the video using ffmpeg."""
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", video_path,
            "-vf", f"ass={ass_path}:fontsdir={FONTS_DIR}",
            output_path
        ], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to burn subtitles into video.")
        exit(1)


def main():
    settings = get_user_inputs()

    print("🎬 Extracting audio...")
    extract_audio(settings["video_path"], settings["audio_path"])

    print("🧠 Running speech-to-text...")
    model = WhisperModel(MODEL_SIZE, compute_type="int8")
    segments, _ = model.transcribe(settings["audio_path"], language=settings["lang"])

    # If you ever want to load an existing .srt file instead:
    # segments = parse_srt_to_segments("my_subs.srt")

    print("📝 Creating subtitle file...")
    create_ass_file(segments, settings)

    print("🔥 Burning subtitles into video...")
    burn_subtitles(settings["video_path"], ASS_PATH, settings["output_path"])

    print(f"✅ Done! Output saved to {settings['output_path']}")


if __name__ == "__main__":
    main()