import os

import edge_tts
import uvicorn


import uuid

import aiofiles
import ffmpeg
from edge_tts import VoicesManager

from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette.websockets import WebSocket

import schemas
from config.base import settings, TEMP_FOLDER_PATH, BASE_DOMAIN
from model import TTSItem, TTSVoiceItem
from service import inference_pipeline_punc, inference_pipeline_asr

from funasr_service import FunASR
from tts_service import TTSService
from utils import base64_decode, base64_encode

app = FastAPI(title="ASR & TTS", summary="ASR & TTS API", docs_url=None, redoc_url=None)


origins = [
    "*",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# ASR ****************************************
asr = FunASR()


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


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
    communicate = edge_tts.Communicate(tts_item.text, tts_item.voice, proxy="http://vpnproxy.hxq.cn:16397")
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
async def api_tts_from_base64(asr_req: schemas.ASRRequest):
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


@app.post("/api/tts")
async def api_tts_to_base64(tts_req: schemas.TTSRequest):
    resp = {
        "code": 0,
        "message": "操作成功！",
        "success": True,
        "data": {"base64": "", "format": "wav"},
    }
    tts_service = TTSService(
        text=tts_req.text,
        voice=tts_req.voice,
        speed=tts_req.speed,
        volume=tts_req.volume,
    )
    b_wav_data = await tts_service.get_tts_wav_data()
    resp["data"] = {"base64": base64_encode(b_wav_data), "format": "wav"}
    return resp


@app.get("/api/tts_voices")
async def api_tts_voices():
    resp = {"code": 0, "message": "操作成功！", "success": True, "data": {"voice_list": []}}
    voice_list = [
        {"id": 1, "value": "xinxin", "label": "心心", "comment": "女声"},
        {"id": 2, "value": "langlang", "label": "朗朗", "comment": "男声"},
    ]
    resp["data"] = {"voice_list": voice_list}
    return resp


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    pass


if __name__ == "__main__":
    uvicorn.run(app="__main__:app", host=settings.HOST, port=settings.PORT, reload=True)
