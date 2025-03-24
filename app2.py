import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from yt_dlp import YoutubeDL
import os
import random

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (update this for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36",
]

DOWNLOAD_PATH = "downloads/audio.mp3"

def download_audio(youtube_url: str):
    """Download audio from YouTube and overwrite the file."""
    # Delete old file before downloading
    if os.path.exists(DOWNLOAD_PATH):
        os.remove(DOWNLOAD_PATH)

    temp_path = f"downloads/temp_{int(time.time())}.mp3"  # Temporary unique filename

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "extract_audio": True,
        "audio_format": "mp3",
        "outtmpl": temp_path,  # Use temporary file
        "noplaylist": True,
        "force_overwrites": True,
        "no-cache-dir": True,
        "cookiefile": "cookies.txt",
        "http_headers": {"User-Agent": random.choice(user_agents)}
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    # Rename the downloaded file to the fixed path
    if os.path.exists(temp_path):
        os.rename(temp_path, DOWNLOAD_PATH)

    return DOWNLOAD_PATH

@app.get("/stream_audio")
async def stream_audio(youtube_url: str):
    """Serve the downloaded audio file."""
    try:
        # Download and overwrite existing file
        audio_file = download_audio(youtube_url)

        # Serve the file with a no-cache response
        return FileResponse(
            audio_file,
            media_type="audio/mpeg",
            filename="audio.mp3",
            headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
        )
    except Exception as e:
        return {"error": str(e)}