# ScribeFlow: Automatic Video Subtitle Generator

**ScribeFlow** is a Python-based tool that automatically generates subtitles for videos using advanced speech-to-text technology and burns them directly into the video. It is designed to be user-friendly, fully customizable, and supports multiple languages and subtitle styles.

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
   git clone https://github.com/yourusername/ScribeFlow.git
   cd ScribeFlow
   ```
2. **Install dependencies using `uv`:**

   ```bash
   uv venv
   uv pip install -r requirements.txt
   ```
3. **Install ffmpeg** (if not already installed):

   * Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   * Add the ffmpeg binary to your system PATH

---

## Usage

1. **Start the API Server:**

   ```bash
   # Run directly (Defaults to Port 5000)
   python app/main.py
   
   # Or using uvicorn directly
   uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
   ```

2. **Access the API:**
   * Open [http://localhost:5000/docs](http://localhost:5000/docs) to see the interactive API documentation.
   * Use the `/generate` endpoint to upload a video and configure subtitles.

---

## Folder Structure

```
.
├── app/           # FastAPI Application
│   ├── main.py    # Entry point & API routes
│   ├── services.py # Core logic
│   ├── schemas.py # Pydantic models
│   └── config.py  # Settings
├── audio/         # Extracted audio files
├── fonts/         # Custom fonts
├── outputs/       # Final videos
├── subtitles/     # .ass subtitle files
├── temp/          # Temporary uploads
├── tests/         # Pytest suite
├── videos/        # Input videos (for manual testing)
├── sub_generater.bak # Backup of original script
├── requirements.txt
└── README.md
```

---

## Advanced Notes

* **Cross-Platform Path Handling:** ScribeFlow automatically formats paths for ffmpeg to avoid errors on Windows (`\` → `/`).
* **Loading Existing Subtitles:** You can skip transcription and load an existing `.srt` file by modifying `parse_srt_to_segments("my_subs.srt")`.
* **Batch Processing:** The code structure allows iterating over multiple videos in `videos/` and generating subtitles in one run.

---

## Contributing

Contributions are welcome!

* Bug reports: Open an issue
* Feature requests: Open an issue or pull request
* Code contributions: Fork the repo, make changes, and submit a pull request
* Major Contributor: <a href="https://github.com/dreww01">Dreww01<a>

---

## License

Provided as-is for educational and personal use. See LICENSE file for details.

---

## Credits

* [OpenAI Whisper](https://github.com/openai/whisper)
* [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
* [FFmpeg](https://ffmpeg.org/)


````
