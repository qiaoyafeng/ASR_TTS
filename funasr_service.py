import logging
import uuid

import ffmpeg
import aiofiles
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from modelscope.utils.logger import get_logger

logger = get_logger(log_level=logging.CRITICAL)
logger.setLevel(logging.CRITICAL)


"""
该类主要是调用FunASR 加载训练好的算法模型，输入音频数据输出文本信息。
"""


class FunASR:
    """
    在_init__中对模型文件进行加载，并...。
    """

    def __init__(
        self,
        asr_model="damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
        punc_model="damo/punc_ct-transformer_zh-cn-common-vad_realtime-vocab272727",
        ngpu=1,
        ncpu=4,
    ):
        self.asr_model = asr_model
        self.punc_model = punc_model
        self.ngpu = ngpu
        self.ncpu = ncpu
        self.inference_pipeline_asr = self.get_inference_pipeline_asr()
        self.inference_pipeline_punc = self.get_inference_pipeline_punc()

    def get_inference_pipeline_asr(self):
        return pipeline(
            task=Tasks.auto_speech_recognition,
            model=self.asr_model,
            ngpu=self.ngpu,
            ncpu=self.ncpu,
            model_revision=None,
        )

    def get_inference_pipeline_punc(self):
        return pipeline(
            task=Tasks.punctuation,
            model=self.punc_model,
            model_revision="v1.0.2",
            ngpu=self.ngpu,
            ncpu=self.ncpu,
        )

    async def recognition_from_bytes(self, audio, add_pun: int = 1):
        print(f"recognition_from_bytes ...")

        # audio_path = f"asr_example_zh.wav"
        audio_path = f"asr.wav"
        async with aiofiles.open(audio_path, "wb") as out_file:
            await out_file.write(audio)

        audio_bytes, _ = (
            ffmpeg.input(audio_path, threads=0)
            .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=16000)
            .run(cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True)
        )

        print(
            f"audio_bytes: audio_bytes type:{type(audio_bytes)} , len:{len(audio_bytes)}"
        )

        rec_result = self.inference_pipeline_asr(audio_in=audio_bytes, param_dict={})
        if add_pun:
            rec_result = self.inference_pipeline_punc(
                text_in=rec_result["text"], param_dict={"cache": list()}
            )
        ret = {"results": rec_result["text"], "code": 0}
        print(ret)
        return ret
