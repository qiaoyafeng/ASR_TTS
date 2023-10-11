FROM python:3.10.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc ffmpeg

# make sure to use venv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"


WORKDIR /opt/asr_tts

COPY ./requirements.txt /opt/asr_tts/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /opt/asr_tts/requirements.txt  -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn

CMD ["/bin/bash"]