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
        speed: float = 1.0,
        volume: float = 1.0,
    ):
        self.text = text
        self.voice = voice
        self.speed = speed
        self.volume = volume

    async def get_tts_wav_data(self):
        audio_name = f"{uuid.uuid4().hex}.wav"
        audio_path = f"{TEMP_FOLDER_PATH}/{audio_name}"
        communicate = edge_tts.Communicate(text=self.text, voice=self.voice)
        await communicate.save(audio_path)
        audio, sampling_rate = soundfile.read(audio_path)

        audio_16k_name = f"{uuid.uuid4().hex}.wav"
        audio_16k_path = f"{TEMP_FOLDER_PATH}/{audio_16k_name}"

        # 模型需要16位的音频文件
        soundfile.write(audio_16k_path, audio, sampling_rate, subtype="PCM_16")
        with open(audio_16k_path, "rb") as fd:
            tts_wav_data = fd.read()
        return tts_wav_data
