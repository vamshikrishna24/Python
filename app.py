from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from yt_dlp import YoutubeDL

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to ["http://localhost:3000"] for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get_audio_url/")
async def get_audio_url(youtube_url: str):
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "extract_flat": False
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            audio_url = info.get("url", None)

        if audio_url:
            return {"audio_url": audio_url}
        else:
            return {"error": "Audio URL not found"}
    
    except Exception as e:
        return {"error": str(e)}
