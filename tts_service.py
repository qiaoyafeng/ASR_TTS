import edge_tts
import soundfile


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
        communicate = edge_tts.Communicate(text=self.text, voice=self.voice)
        await communicate.save("tts.wav")
        audio, sampling_rate = soundfile.read("tts.wav")

        # 模型需要16位的音频文件
        soundfile.write("16tts.wav", audio, sampling_rate, subtype="PCM_16")
        with open("16tts.wav", "rb") as fd:
            tts_wav_data = fd.read()
        return tts_wav_data
