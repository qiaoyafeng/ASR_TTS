from pydantic import BaseModel


class TTSItem(BaseModel):
    text: str
    voice: str = "zh-CN-XiaoxiaoNeural"


class TTSVoiceItem(BaseModel):
    Language: str = ""  # "Language": "zh" "en"
    Locale: str = ""  # "Locale": "zh-CN", "zh-HK",
    Gender: str = ""  # "Gender": "Female","Male",
