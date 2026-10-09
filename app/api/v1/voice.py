import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
from app.voice.openai_audio import OpenAIAudioService
from app.voice.listing_extractor import ListingExtractor
from app.core.settings import settings

router = APIRouter(prefix='/voice', tags=['Voice AI'])


@router.post('/transcribe')
async def transcribe(file: UploadFile = File(...), language: str | None = Form(default=None)):
    suffix = os.path.splitext(file.filename or 'audio.wav')[1] or '.wav'
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        path = tmp.name
    try:
        text = await OpenAIAudioService().transcribe(path, language)
        return {'transcript': text}
    finally:
        os.unlink(path)


@router.post('/listing-extract')
async def listing_extract(file: UploadFile = File(...), language: str | None = Form(default=None)):
    suffix = os.path.splitext(file.filename or 'audio.wav')[1] or '.wav'
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        path = tmp.name
    try:
        text = await OpenAIAudioService().transcribe(path, language)
        data = await ListingExtractor().extract(text)
        return {'transcript': text, 'extracted': data, 'requires_confirmation': True}
    finally:
        os.unlink(path)


@router.post('/tts')
async def tts(text: str = Form(...), voice: str | None = Form(default=None)):
    os.makedirs(settings.media_dir, exist_ok=True)
    fd, path = tempfile.mkstemp(prefix='tts_', suffix='.mp3', dir=settings.media_dir)
    os.close(fd)
    await OpenAIAudioService().synthesize(text, path, voice)
    return FileResponse(path, media_type='audio/mpeg', filename='speech.mp3')
