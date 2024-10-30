import uuid

import edge_tts
import soundfile

from config.base import TEMP_FOLDER_PATH


class TTSService:
    """
    TTSService
    """

    def __init__(
        self,
        text: str = "",
        voice: str = "zh-CN-XiaoxiaoNeural",
        speed: float = 0.0,
        volume: float = 0.0,
    ):
        self.text = text
        self.voice = voice
        self.speed = f"+{int(speed*100)}%" if speed >= 0 else f"{int(speed*100)}%"
        self.volume = f"+{int(volume*100)}%" if volume >= 0 else f"{int(volume*100)}%"

    async def get_tts_wav_data(self):
        audio_name = f"{uuid.uuid4().hex}.wav"
        audio_path = f"{TEMP_FOLDER_PATH}/{audio_name}"
        communicate = edge_tts.Communicate(text=self.text, voice=self.voice, rate=self.speed, volume=self.volume, proxy="http://vpnproxy.hxq.cn:16397")
        await communicate.save(audio_path)
        audio, sampling_rate = soundfile.read(audio_path)

        audio_16k_name = f"{uuid.uuid4().hex}.wav"
        audio_16k_path = f"{TEMP_FOLDER_PATH}/{audio_16k_name}"

        # 模型需要16位的音频文件
        soundfile.write(audio_16k_path, audio, sampling_rate, subtype="PCM_16")
        with open(audio_16k_path, "rb") as fd:
            tts_wav_data = fd.read()
        return tts_wav_data
