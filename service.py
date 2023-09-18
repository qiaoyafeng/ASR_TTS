import logging
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from modelscope.utils.logger import get_logger

logger = get_logger(log_level=logging.CRITICAL)
logger.setLevel(logging.CRITICAL)


asr_model = "damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"
punc_model = "damo/punc_ct-transformer_zh-cn-common-vad_realtime-vocab272727"
gpu_count = 1
cpu_count = 4


print("model loading")

# asr
inference_pipeline_asr = pipeline(
    task=Tasks.auto_speech_recognition,
    model=asr_model,
    ngpu=gpu_count,
    ncpu=cpu_count,
    model_revision=None,
)
print(f"loaded asr models.")

inference_pipeline_punc = pipeline(
    task=Tasks.punctuation,
    model=punc_model,
    model_revision="v1.0.2",
    ngpu=gpu_count,
    ncpu=cpu_count,
)
print(f"loaded pun models.")
