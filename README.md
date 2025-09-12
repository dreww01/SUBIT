# SUBIT: Automatic Video Subtitle Generator

**SUBIT** is a Python-based tool that automatically generates subtitles for videos using advanced speech-to-text technology and burns them directly into the video. It is designed to be user-friendly, fully customizable, and supports multiple languages and subtitle styles.

---

## Features

- **Automatic Speech Recognition:** Uses [Whisper](https://github.com/openai/whisper) via [faster-whisper](https://github.com/SYSTRAN/faster-whisper) for fast and accurate transcription.
- **Subtitle Generation:** Produces `.ass` (Advanced SubStation Alpha) subtitle files with highly customizable styles and effects.
- **Subtitle Burning:** Hardcodes subtitles directly into the video using [ffmpeg](https://ffmpeg.org/).
- **Customizable Appearance:** Configure font, color, size, weight, shadow, position, and optional animated "bounce" effect.
- **Multi-language Support:** Supports English (`en`), Thai (`th`), Japanese (`ja`), and Chinese (`zh`).
- **Video Selection:** Automatically detects videos in the `videos/` folder or allows manual  selection.
- **Batch-Processing Ready:** Easily extendable for batch or automated workflows.
- **Cross-Platform Compatible:** Works on Windows, macOS, and Linux (paths are automatically formatted for ffmpeg).

---

## Requirements

- Python 3.8 or higher
- [ffmpeg](https://ffmpeg.org/) installed and added to your system PATH
- Python dependencies (install via `requirements.txt`):
  - `faster-whisper`
  - `ctranslate2`
  - `pysrt`
  - (other dependencies as listed in `requirements.txt`)

---

## Installation

1. **Clone or download the repository:**
   ```bash
   git clone https://github.com/yourusername/SUBIT.git
   cd SUBIT
   ```

````

2. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```
3. **Install ffmpeg** (if not already installed):

   * Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   * Add the ffmpeg binary to your system PATH so it can be accessed from the terminal/command prompt

---

## Usage

1. **Place your video files** in the `videos/` folder. Supported formats: `.mp4`, `.mov`, `.avi`, `.mkv`, `.flv`, `.wmv`.

2. **Run the script:**

   ```bash
   python sub_generater.py
   ```

3. **Follow the interactive prompts:**

   * Select the video to process (if multiple are detected)
   * Choose subtitle options (font, color, size, position, bounce effect)
   * Select the transcription language

4. **Output:**

   * Final video with burned-in subtitles saved in the `outputs/` folder
   * Generated `.ass` subtitle file saved in the `subtitles/` folder
   * Extracted audio saved in the `audio/` folder

---

## Customization Options

* **Font:** Place custom fonts in the `fonts/` folder. Default font is `Playfair Display`.
* **Colors:** Choose from predefined names (`yellow`, `white`, `cyan`, etc.) or use hex codes (`#FFFF00`).
* **Subtitle Position:** Bottom, middle, top, or slightly above the bottom.
* **Bounce Effect:** Optional animated scaling effect for each subtitle chunk.
* **Words per Line:** Control the number of words displayed per subtitle line for readability.

---

## Example Workflow

1. Add your video `myvideo.mp4` to `videos/`.
2. Run the script:

   ```bash
   python sub_generater.py
   ```
3. Configure your subtitles via prompts: color, font, size, position, and language.
4. Wait for the process to complete.
5. Check the `outputs/` folder for the subtitled video and `subtitles/` folder for the `.ass` file.

---

## Troubleshooting

* **ffmpeg not found:** Ensure ffmpeg is installed and added to the system PATH.
* **No video files found:** Make sure there is at least one supported video file in `videos/`.
* **Whisper model errors:** Check that all dependencies are installed correctly (`faster-whisper`, `ctranslate2`).
* **Font not found:** Confirm the font file exists in the `fonts/` folder.
* **Subtitle not displaying or double subtitles:** Ensure paths use forward slashes (`/`) for Windows compatibility.

---

## Folder Structure

```
.
├── audio/         # Extracted audio files
├── fonts/         # Custom fonts for subtitles
├── outputs/       # Final videos with burned-in subtitles
├── subtitles/     # Generated .ass subtitle files
├── videos/        # Input video files
├── sub_generater.py  # Main script
├── requirements.txt  # Python dependencies
└── README.md
```

---

## Advanced Notes

* **Cross-Platform Path Handling:** SUBIT automatically formats paths for ffmpeg to avoid errors on Windows (`\` → `/`).
* **Loading Existing Subtitles:** You can skip transcription and load an existing `.srt` file by modifying `parse_srt_to_segments("my_subs.srt")`.
* **Batch Processing:** The code structure allows iterating over multiple videos in `videos/` and generating subtitles in one run.

---

## Contributing

Contributions are welcome!

* Bug reports: Open an issue
* Feature requests: Open an issue or pull request
* Code contributions: Fork the repo, make changes, and submit a pull request

---

## License

Provided as-is for educational and personal use. See LICENSE file for details.

---

## Credits

* [OpenAI Whisper](https://github.com/openai/whisper)
* [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
* [FFmpeg](https://ffmpeg.org/)


````
