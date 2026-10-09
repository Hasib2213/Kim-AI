import os
import tempfile
from fastapi import APIRouter, UploadFile, File
from app.media_ai.image_analysis import analyze_property_image
from app.media_ai.video_analysis import analyze_property_video

router = APIRouter(prefix='/media-ai', tags=['Media AI'])


async def _save_temp(file: UploadFile):
    suffix = os.path.splitext(file.filename or 'upload.bin')[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        return tmp.name


@router.post('/image/analyze')
async def image_analyze(file: UploadFile = File(...)):
    path = await _save_temp(file)
    try:
        return await analyze_property_image(path)
    finally:
        os.unlink(path)


@router.post('/video/analyze')
async def video_analyze(file: UploadFile = File(...)):
    path = await _save_temp(file)
    try:
        return await analyze_property_video(path)
    finally:
        os.unlink(path)
