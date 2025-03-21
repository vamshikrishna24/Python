from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from yt_dlp import YoutubeDL  # Use yt-dlp
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
        # Options for yt-dlp
        ydl_opts = {
            "format": "bestaudio/best",  # Get the best audio quality
            "quiet": True,  # Suppress output
            "extract_flat": False,  # Ensure full metadata is extracted
            "cookiefile": "cookies.txt",  # Optional: Use cookies if needed
            "noplaylist": True,  # Ensure only single videos are processed
        }

        # Extract audio URL using yt-dlp
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            formats = info.get('formats', [])
            audio_url = None

            # Find the best audio-only format
            for f in formats:
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    audio_url = f.get('url')
                    break

        if audio_url:
            # Add required headers for the audio URL to be playable
            headers = {
                "Referer": "https://www.youtube.com/",  # Required by YouTube
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",  # Mimic a browser
            }

            # Verify that the URL is playable by making a test request
            response = requests.get(audio_url, headers=headers, stream=True)
            if response.status_code == 200:
                return {"audio_url": audio_url, "headers": headers}  # Return the URL and headers
            else:
                return {"error": "Audio URL is not playable", "status_code": response.status_code}
        else:
            return {"error": "Audio URL not found"}
    
    except Exception as e:
        return {"error": str(e)}