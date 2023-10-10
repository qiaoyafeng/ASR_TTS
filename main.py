import os

import edge_tts
import uvicorn


import uuid

import aiofiles
import ffmpeg
from edge_tts import VoicesManager

from fastapi import FastAPI, UploadFile, File, Body
from starlette.responses import FileResponse
from starlette.websockets import WebSocket

import schemas
from config.base import settings, TEMP_FOLDER_PATH, BASE_DOMAIN
from model import TTSItem, TTSVoiceItem
from service import inference_pipeline_punc, inference_pipeline_asr

from funasr_service import FunASR
from utils import base64_decode

app = FastAPI(title="ASR & TTS", summary="ASR & TTS API")


# ASR ****************************************
asr = FunASR()


@app.get("/get_file/{file_name}")
def read_item(file_name: str):
    file_path = os.path.isfile(os.path.join(TEMP_FOLDER_PATH, file_name))
    if file_path:
        return FileResponse(os.path.join(TEMP_FOLDER_PATH, file_name))
    else:
        return {"code": 404, "message": "file does not exist."}


@app.post("/tts")
async def api_tts(tts_item: TTSItem):
    audio_name = f"{str(uuid.uuid1())}.wav"
    audio_path = f"{TEMP_FOLDER_PATH}/{audio_name}"
    communicate = edge_tts.Communicate(tts_item.text, tts_item.voice)
    await communicate.save(audio_path)
    audio_url = f"{BASE_DOMAIN}/get_file/{audio_name}"
    return {"audio_url": audio_url}


@app.post("/tts_voices")
async def api_tts_voices(tts_voice_item: TTSVoiceItem):
    voices = await VoicesManager.create()
    print(f"11111,{voices}")
    filter_dict = tts_voice_item.model_dump()
    print(f"filter_dict: {filter_dict}")
    filter_dict = {k: v for k, v in filter_dict.items() if v}
    voices = voices.find(**filter_dict)
    print(f"22222,{voices}")
    return voices


@app.post("/asr")
async def api_asr(
    audio: UploadFile = File(..., description="audio file"),
    add_pun: int = Body(1, description="add punctuation", embed=True),
):
    suffix = audio.filename.split(".")[-1]
    audio_path = f"{TEMP_FOLDER_PATH}/{str(uuid.uuid1())}.{suffix}"
    async with aiofiles.open(audio_path, "wb") as out_file:
        content = await audio.read()
        await out_file.write(content)
    audio_bytes, _ = (
        ffmpeg.input(audio_path, threads=0)
        .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=16000)
        .run(cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True)
    )
    rec_result = inference_pipeline_asr(audio_in=audio_bytes, param_dict={})
    if add_pun:
        rec_result = inference_pipeline_punc(
            text_in=rec_result["text"], param_dict={"cache": list()}
        )
    ret = {"results": rec_result["text"], "code": 0}
    print(ret)
    return ret


@app.post("/api/asr")
async def api_asr_from_base64(asr_req: schemas.ASRRequest):
    resp = {
        "code": 0,
        "message": "操作成功！",
        "success": True,
        "data": {"text": ""},

    }
    audio_bytes = base64_decode(asr_req.audio_base64)
    recognition_data = await asr.recognition_from_bytes(audio_bytes)
    resp["data"] = {"text": recognition_data["results"]}
    return resp


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    pass


if __name__ == "__main__":
    uvicorn.run(app="__main__:app", host=settings.HOST, port=settings.PORT, reload=True)
