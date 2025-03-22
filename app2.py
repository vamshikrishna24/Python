from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from yt_dlp import YoutubeDL
import requests
import subprocess

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to ["http://localhost:3000"] for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get_audio_url")
async def get_audio_url(youtube_url: str):
    print("jello")
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "extract_flat": False,
            "cookiefile": "cookies.txt",
            "noplaylist": True,
            "extractor_args": {"youtube": {"music": True}},
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            formats = info.get('formats', [])
            audio_url = None
            for f in formats:
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    audio_url = f.get('url')
                    break

        if audio_url:
            return {"audio_url": audio_url}
        else:
            return {"error": "Audio URL not found"}
    
    except Exception as e:
        return {"error": str(e)}