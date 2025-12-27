# ScribeFlow Architecture Documentation

This document provides a detailed architectural map of the ScribeFlow project, an automatic video subtitle generator.

## 1. High-Level Overview

ScribeFlow is a Python-based application that processes video files to automatically generate and burn hardcoded subtitles. It leverages **faster-whisper** for speech-to-text transcription and **FFmpeg** for media processing (audio extraction and subtitle burning).

The project offers two primary interfaces:
1.  **CLI (Command Line Interface)**: A standalone script for local, interactive usage.
2.  **REST API**: A FastAPI-based web service for programmatic video processing.

## 2. System Architecture

### 2.1 Core Workflow pipeline
Regardless of the interface used, the core processing pipeline follows these steps:

1.  **Input**: Video file + Configuration (Language, Color, Font, etc.)
2.  **Audio Extraction**: FFmpeg extracts audio track from video to WAV format.
3.  **Transcription**: Faster-Whisper model processes the WAV file to generate timestamped text segments.
4.  **Subtitle Generation**: Text segments are formatted into an `.ass` (Advanced SubStation Alpha) file, applying specific styles (colors, shadows, animations).
5.  **Subtitle Burning**: FFmpeg renders the `.ass` subtitles onto the original video.
6.  **Output**: Final video file with hardcoded subtitles.

### 2.2 Component Diagram

```mermaid
graph TD
    User([User])
    
    subgraph Interfaces
        CLI[CLI Script\n(sub_generater.py)]
        API[FastAPI App\n(app/main.py)]
    end
    
    subgraph "Core Services (app/services.py)"
        ModelMgr[ModelManager\n(Whisper Loading)]
        Extractor[Audio Extractor]
        Generator[Subtitle Generator\n(Logic)]
        Renderer[ASS Creator]
        Burner[Subtitle Burner]
    end
    
    subgraph "External Tools"
        Whisper[Faster-Whisper\n(Local AI Model)]
        FFmpeg[FFmpeg\n(Media Processing)]
    end

    User --> CLI
    User --> API
    
    API --> ModelMgr
    API --> Extractor
    API --> Generator
    API --> Renderer
    API --> Burner
    
    CLI -.->|Duplicated Logic| Extractor
    CLI -.->|Duplicated Logic| Whisper
    CLI -.->|Duplicated Logic| FFmpeg
    
    ModelMgr --> Whisper
    Extractor --> FFmpeg
    Burner --> FFmpeg
```

> **Note**: Currently, `sub_generater.py` operates as a standalone script with its own implementation of the core logic, while the `app/` directory contains a modularized version of similar logic.

## 3. Directory Structure & Key Files

### Root Directory
*   `sub_generater.py`: **Main CLI Entry Point**. Contains the interactive CLI loop and a standalone implementation of the processing pipeline.
*   `requirements.txt`: Project dependencies.
*   `check_env.py`: Utility to verify environment setup.

### `app/` (API Package)
*   `main.py`: **API Entry Point**. Defines FastAPI routes (`/generate`) and manages request lifecycle.
*   `services.py`: **Business Logic**.
    *   `ModelManager`: Singleton class to manage the Whisper model state (loading/unloading, GPU/CPU).
    *   `extract_audio()`: Wrapper for FFmpeg audio extraction.
    *   `generate_subtitles()`: Wrapper for Whisper transcription.
    *   `create_ass_file()`: Generates `.ass` file content from segments.
    *   `burn_subtitles()`: Wrapper for FFmpeg to burn subtitles.
*   `schemas.py`: **Data Models**. Pydantic models (e.g., `SubtitleConfig`) for request validation.
*   `config.py`: Configuration constants (paths, defaults).

### Data Directories
*   `videos/`: Input directory for the CLI tool.
*   `outputs/`: Destination for processed videos.
*   `audio/`: Intermediate storage for extracted WAV files.
*   `subtitles/`: Intermediate storage for generated `.ass` files.
*   `fonts/`: Directory for custom fonts used in subtitle rendering.
*   `temp/`: Temporary storage for API uploads.

## 4. Technology Stack

*   **Language**: Python 3.8+
*   **Web Framework**: FastAPI, Uvicorn (for API)
*   **AI/ML**: 
    *   `faster-whisper`: Optimized Whisper implementation using CTranslate2 for fast inference.
    *   `ctranslate2`: Transformer inference engine.
*   **Media Processing**: 
    *   `ffmpeg-python` / `subprocess`: Interfacing with system FFmpeg binary.
*   **Validation**: Pydantic

## 5. Data Flow Details (API)

1.  **Request**: Client sends `POST /generate` with `video` (file) and `config_json` (stringified JSON).
2.  **Validation**: `app.main` parses `config_json` using `SubtitleConfig`.
3.  **File Handling**: Video is saved to `temp/`.
4.  **Processing**: `app.services` functions are called sequentially.
5.  **Cleanup**: Intermediate files (audio, temp video) are removed (optional/configurable).
6.  **Response**: Processed video is streamed back as `FileResponse`.

## 6. Future Considerations

*   **Unification**: Refactoring `sub_generater.py` to import logic from `app/services.py` would reduce code duplication and improve maintainability.
*   **Queueing**: For high load, the API might need a task queue (e.g., Celery/Redis) instead of processing synchronously.
*   **Storage**: Moving from local file system storage to cloud storage (S3) for scalable API deployment.
