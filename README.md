# Intel NPU - vlc player with generated subtitles by OpenAI-Whisper  

A python vlc player that transcribes subtitles while watching a video. The model used to automatically generate the subtitles is the tiny version of [Whisper, by Open-AI](https://openai.com/index/whisper) for low memory impact, which doesn't have a translation capability, so the subtitle translations are done using the `google-trans` package . 
The Whisper model is compiled using the [Intel® NPU Acceleration Library](https://github.com/intel/intel-npu-acceleration-library), so that it ultimately runs on the Intel NPU, releaving the CPU or GPU of the processing for a low-powered and efficient inference.

## Content

`./src` : source files of the application

`./media` : various media files used by the project, including a test video file

## Prerequisites

For the application to run properly, install the following prerequisites:
    - the [VLC](https://www.videolan.org/) media player, as the python package is just an API
    - the [FFmpeg](https://ffmpeg.org/) suite for proper handling of video and audio files.

## Installation
The video player runs on the [python3](https://www.python.org/downloads/) programming language. Testing was done on version 3.10.11.

Package requirements:
```bash
googletrans==3.0.0
PyQt6==6.6.1
torch==1.11.0
intel_npu_acceleration_library==1.0.0
openai-whisper==20231117
python-vlc==3.0.20123
```

Install:
```bash
pip install -r /src/requirements.txt

```

## Usage

The app GUI can be started by running the `main.py` file:

```bash
python src/main.py
```

Usage example:
![alt text](./media/run_example.png)
