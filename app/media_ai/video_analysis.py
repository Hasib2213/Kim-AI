import asyncio
import tempfile
from pathlib import Path
from app.core.settings import settings
from app.voice.openai_audio import OpenAIAudioService
from app.voice.listing_extractor import ListingExtractor


async def analyze_property_video(file_path: str) -> dict:
    audio = OpenAIAudioService()
    extractor = ListingExtractor()
    with tempfile.TemporaryDirectory() as td:
        audio_path = str(Path(td) / 'audio.mp3')
        proc = await asyncio.create_subprocess_exec(
            settings.ffmpeg_binary, '-y', '-i', file_path, '-vn', '-acodec', 'libmp3lame', audio_path,
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
        )
        rc = await proc.wait()
        if rc != 0 or not Path(audio_path).exists():
            return {'transcript': '', 'listing': {}, 'warning': 'Could not extract audio. Install ffmpeg and verify the video file.'}
        transcript = await audio.transcribe(audio_path)
        listing = await extractor.extract(transcript)
        return {'transcript': transcript, 'listing': listing}
