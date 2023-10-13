# ASR and TTS
<p align="left">
    <a href=""><img src="https://img.shields.io/badge/Python->=3.7,<=3.10-aff.svg"></a>
    <a href=""><img src="https://img.shields.io/badge/Pytorch-%3E%3D1.11-blue"></a>
</p>


<div align="center">  
<h4>
｜<a href="#安装"> 安装 </a>
｜<a href="#启动"> 启动 </a>
</h4>
</div>


## 安装

 pip install -r requirements.txt


## 启动

### FastAPI方式启动HTTP服务

```shell
uvicorn main:app --reload --host=0.0.0.0 --port=32101
```


### 在Linux服务器运行

```shell

nohup uvicorn main:app --reload --host=0.0.0.0 --port=32101 > uvicorn.log 2>&1 &

```




