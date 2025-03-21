
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from yt_dlp import YoutubeDL
import requests

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
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "extract_flat": False,
            "cookiefile": "cookies.txt",
            "noplaylist": True,
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
    


def get_audio_stream(url):
    """ Generator function to stream audio in chunks """
    ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "extract_flat": False,
            "cookiefile": "cookies.txt",
            "noplaylist": True,
        }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get("formats", [])
        
        audio_url = None
        for f in formats:
            if f.get("vcodec") == "none" and f.get("acodec") != "none":
                audio_url = f.get("url")
                break

    if not audio_url:
        raise Exception("Audio URL not found")

    # ✅ FIX: The function must return an actual generator, not a function reference
    def iter_chunks():
        with requests.get(audio_url, stream=True) as r:
            r.raise_for_status()  # Ensures request was successful
            for chunk in r.iter_content(chunk_size=1024 * 256):  # 256KB chunks
                if chunk:
                    yield chunk

    return iter_chunks()  # ✅ Call the function to return a generator

@app.get("/stream_audio")
async def stream_audio(youtube_url: str):
    try:
        return StreamingResponse(get_audio_stream(youtube_url), media_type="audio/mpeg")
    except Exception as e:
        return Response(f"Error: {str(e)}", status_code=500)