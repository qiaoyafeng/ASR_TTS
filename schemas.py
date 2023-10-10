from pydantic import BaseModel


class ASRRequest(BaseModel):
    audio_base64: str
    add_pun: int = 1


class TTSRequest(BaseModel):
    text: str
    voice: str = "zh-CN-XiaoxiaoNeural"
    speed: float = 1.0
    volume: float = 1.0
