
# SUBIT- A Subtitle Generation System – Requirements

## Overview

We are building a **video subtitle generation platform** where users can upload a video, customize subtitle styles (font, color, position, etc.), and generate output videos with subtitles.

The system should produce **two versions of the video**:

1. **Watermarked video** → For preview on the frontend.
2. **Non-watermarked video** → Available only after the user pays with credits.

Because of limited processing power, the backend can only process **one video at a time**. A **queue system** is required to manage multiple requests.

---

## User Flow

1. **Upload Video**

   * User uploads a video file on the "Generation Page".
   * User selects subtitle settings:

     * Font family
     * Font size
     * Font color
     * Position (top, bottom, custom X/Y offset)
     * Optional style attributes (bold, italic, background, shadow, etc.)

2. **Generate Request**

   * User clicks "Generate".
   * Request is sent to backend with:

     * Uploaded video file path
     * Subtitle file (or generated text)
     * Style configuration

3. **Queue Handling**

   * The backend adds the request to a **FIFO queue**.
   * If the system is busy, the request waits until earlier jobs are processed.
   * When it’s the job’s turn, the backend starts processing.

4. **Processing**

   * The backend uses **FFmpeg** to:

     * Burn subtitles into the video (with chosen styles).
     * Output **two files**:

       1. `with_watermark.mp4`
       2. `without_watermark.mp4`

5. **Frontend Preview**

   * Once the watermarked video is ready, it is uploaded to the frontend.
   * The user previews the result.

6. **Watermark Removal (Payment)**

   * If satisfied, the user clicks **“Remove Watermark”**.
   * Payment of **30 credits** is deducted from their balance.
   * Once payment is confirmed, the non-watermarked video is made available for download.

7. **Next Job**

   * After finishing a request, the backend automatically moves on to the next item in the queue.

---

## Technical Requirements

### Backend

* **Language:** Python
* **Framework:** FastAPI (for APIs)
* **Video Processing:** FFmpeg (triggered by Python)
* **Queue:**

  * Start with in-memory FIFO queue.
  * Later upgrade to Redis + worker system (Celery or RQ).

### Frontend

* **Upload UI:** Video upload form with subtitle styling controls.
* **Preview Player:** Plays the watermarked video.
* **Payment Button:** “Remove Watermark” triggers payment + file unlock.

### Storage

* **Temporary Storage:** Local disk for uploaded and processed videos.
* **Optional Future:** Cloud storage (AWS S3, GCP, or similar).

### Payment / Credits

* User must have credits in their account.
* Deduction of **30 credits** when watermark is removed.
* After successful payment, the backend returns a secure link to download the clean video.

---

## Non-Functional Requirements

* Only **one video processes at a time**. Queue ensures fairness.
* Each job should **never block or crash the system**.
* Processing time depends on video length; user should see a “waiting/processing” status.
* Files should be automatically cleaned up after X days to save space.

---

## Deliverables

1. **Frontend (Generation Page):**

   * Upload form + styling options.
   * Preview player for watermarked video.
   * Button for payment and download.

2. **Backend API:**

   * Upload endpoint
   * Generate request endpoint (with queue)
   * Video status endpoint (waiting, processing, done)
   * Payment & unlock endpoint

3. **Queue Worker:**

   * Handles requests sequentially.
   * Uses FFmpeg to produce both videos.
   * Moves to next request after finishing.
