from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from yt_dlp import YoutubeDL
import subprocess

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_best_audio_url(youtube_url: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "extract_flat": False,
        "cookiefile": "cookies.txt",
        "noplaylist": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info.get("url", None)

@app.get("/stream_audio")
async def stream_audio(youtube_url: str):
    print("jello")
    print(youtube_url)
    audio_url = get_best_audio_url(youtube_url)
    
    if not audio_url:
        return {"error": "Audio URL not found"}

    ffmpeg_cmd = [
        "ffmpeg",
        "-i", audio_url,
        "-f", "mp3",  
        "-b:a", "192k",
        "-"
    ]

    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=4096)

    return StreamingResponse(process.stdout, media_type="audio/mpeg")
