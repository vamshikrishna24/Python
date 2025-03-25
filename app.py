import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from yt_dlp import YoutubeDL
import os
import random
import shutil

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (update this for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



DOWNLOAD_PATH = "downloads/audio.mp3"

COOKIES_FILE = "cookies.txt"
COOKIES_COPY = "cookies_copy.txt"

shutil.copy(COOKIES_FILE, COOKIES_COPY)

def download_audio(youtube_url: str,max_retries=3):
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
        "cookiefile": COOKIES_COPY,
        "retries": max_retries,
        "socket_timeout": 30,
        "extractor_retries": 3,
    }

    for attempt in range(max_retries):
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            
            if os.path.exists(temp_path):
                if os.path.exists(DOWNLOAD_PATH):
                    os.remove(DOWNLOAD_PATH)
                os.rename(temp_path, DOWNLOAD_PATH)
                return DOWNLOAD_PATH
            
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = (2 ** attempt) + random.random()
            time.sleep(wait_time)
    
    raise Exception("Max retries exceeded")

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