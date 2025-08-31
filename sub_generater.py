from faster_whisper import WhisperModel
import subprocess
import os

# ----------------- This value can be adjusted -------------------
video_path = "test.mp4"
max_words_per_line = int(input("Word per line: "))
model_size = "small"
subtitle_color = input("Color (Hex For example #FFFF00): ")
font_weight = int(input("Font thickness (100-900, Normal : 400 , 700): "))
font_size = int(input("Font Size ( 48, 64): "))
shadow_strength = float(input("Shadow (0 = None, 1 = Normal, 3 = thick): "))
enable_bounce = input("Bonce effect? (True/False): ").strip().lower() == "true"
lang = input("Languge('th', 'en', 'ja', 'zh'): ").strip().lower()

print("positiion:\n1 = MiddleBottom\n2 = Middle\n3 = MiddleTop\n4 = Middle of MiddleBottom")
position_choice = input("Position (1/2/3/4): ")
alignment_map = {
    "1": 2,  # MiddleBottom 
    "2": 5,  # Middle
    "3": 8,  # MiddleTop
    "4": 5   # Middle of MiddleBottom
}
alignment = alignment_map.get(position_choice, 2)

# Change margin_v here
if position_choice == "4":
    margin_v = 180  # Middle of MiddleBottom
else:
    margin_v = 30

custom_font_name = "Playfair Display"
custom_font_path = "PlayfairDisplay-VariableFont_wght.ttf"
# -------------------------------------------------------

audio_path = "audio.wav"
ass_path = "subtitles.ass"
output_path = "output_with_sub.mp4"

# STEP 1: Extract audio from video
subprocess.run([
    "ffmpeg", "-y", "-i", video_path,
    "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2",
    audio_path
])

# STEP 2: Load model from faster-whisper
model = WhisperModel(model_size, compute_type="int8")  # Use int8 on CPU for faster performance.
segments, _ = model.transcribe(audio_path, language=lang)

# STEP 3: Function to convert time into subtitle format
def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int((seconds - int(seconds)) * 100)
    return f"{hours:01}:{minutes:02}:{secs:02}.{centis:02}"

# STEP 4: create '.ass' file
with open(ass_path, "w", encoding="utf-8") as f:
    f.write("[Script Info]\n")
    f.write("ScriptType: v4.00+\n")
    f.write("PlayResX: 1280\n")
    f.write("PlayResY: 720\n")
    f.write("WrapStyle: 0\n")
    f.write("ScaledBorderAndShadow: yes\n")
    f.write("YCbCr Matrix: TV.601\n\n")

    f.write("[V4+ Styles]\n")
    f.write("Format: Name, Fontname, Fontsize, PrimaryColour, Bold, Italic, Underline, "
            "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
            "Alignment, MarginL, MarginR, MarginV, Encoding\n")

    # Convert color from #RRGGBB to &HBBGGRR
    hex_color = subtitle_color.lstrip("#")
    bgr_hex = f"&H00{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}"

    f.write(f"Style: Default,{custom_font_name},{font_size},{bgr_hex},{font_weight},0,0,0,"
            f"100,100,0,0,1,2,{shadow_strength},{alignment},10,10,{margin_v},1\n")

    f.write("\n[Events]\n")
    f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")

    for segment in segments:
        words = segment.text.strip().split()
        total_words = len(words)
        start_time = segment.start
        end_time = segment.end
        duration = end_time - start_time

        for i in range(0, total_words, max_words_per_line):
            chunk_words = words[i:i + max_words_per_line]
            chunk_len = len(chunk_words)

            avg_word_duration = duration / total_words
            chunk_start = start_time + i * avg_word_duration
            chunk_end = chunk_start + chunk_len * avg_word_duration

            start_str = format_time(chunk_start)
            end_str = format_time(chunk_end)
            text = ' '.join(chunk_words)

            if enable_bounce:
                effect = r"{\fscx30\fscy30\t(0,75,\fscx115\fscy115)\t(75,150,\fscx100\fscy100)}"
                text = f"{effect}{text}"

            f.write(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{text}\n")

# STEP 5: Burn subtitles into video
subprocess.run([
    "ffmpeg", "-y", "-i", video_path,
    "-vf", f"ass={ass_path}:fontsdir=.",
    output_path
])

