# Deploying ScribeFlow to Google Cloud Platform (GCP)

This guide explains how to host your ScribeFlow subtitle generator on GCP.

## 1. Containerization (The Foundation)

We have created a `Dockerfile` in your project root. This packages your code, Python dependencies, and FFmpeg into a single "image" that can run anywhere.

## 2. Recommended Architecture: Cloud Run

For this application, **Google Cloud Run** is the easiest place to start. It scales automatically and you only pay when requests are processing.

### Prerequisites regarding GPU
*   **Standard Cloud Run** uses **cpus**. Your transcription will be slower than on your local GPU, but it will work (Whisper supports CPU automatically).
*   **Cloud Run with GPU** is currently in preview/limited availability.
*   **Alternative**: Use **Google Compute Engine** (VM) if you absolutely need cheap/consistent GPU access (e.g., using a T4 GPU).

## 3. Deployment Steps

### Step A: Enable Google APIs
1.  Go to GCP Console.
2.  Enable **Cloud Run API** and **Artifact Registry API**.

### Step B: Build and Push Docker Image
1.  Install Google Cloud SDK (`gcloud`) on your machine.
2.  Initialize it: `gcloud init`
3.  Create a repository:
    ```bash
    gcloud artifacts repositories create subit-repo --repository-format=docker \
        --location=us-central1 --description="ScribeFlow repository"
    ```
4.  Build and push the image:
    ```bash
    gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/subit-repo/subit-app
    ```

### Step C: Deploy to Cloud Run
Run this command to deploy:

```bash
gcloud run deploy subit-service \
    --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/subit-repo/subit-app \
    --platform managed \
    --region us-central1 \
    --port 5000 \
    --memory 4Gi \
    --cpu 2 \
    --allow-unauthenticated
```

*   **Memory**: We requested `4Gi` because loading the Whisper model and processing video requires RAM.
*   **Timeout**: You may need to increase the timeout (default is 5 mins) for long videos: `--timeout=3000`.

## 4. Important Considerations for production

1.  **Storage**: Cloud Run has an ephemeral filesystem. If the container restarts, files in `outputs/` are lost.
    *   **Solution**: Modify the code to upload the final video to **Google Cloud Storage (GCS)** and return a signed URL instead of `FileResponse`.
2.  **Concurrency**: Video processing is heavy. Set `--concurrency 1` so one container handles one video at a time (Cloud Run will autoscale to handle more users).
