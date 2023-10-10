from pydantic import BaseModel


class ASRRequest(BaseModel):
    audio_base64: str
    add_pun: int = 1
