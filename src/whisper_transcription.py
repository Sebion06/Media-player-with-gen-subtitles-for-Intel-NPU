#!/usr/bin/python
import math
import torch
import whisper
import intel_npu_acceleration_library


def parse_whisper_time_string(time_str):
    hours = 0
    mins = 0
    secs = 0
    ms = 0

    if time_str.count(":") < 2:
        mins, rest = time_str.split(":", 1)
        secs, ms = rest.split(",", 1)
    else:
        hours, rest = time_str.split(":", 1)
        mins, rest = rest.split(":", 1)
        secs, ms = rest.split(",", 1)

    return int(hours), int(mins), int(secs), int(ms)


def times_to_ms(hours, mins, secs, ms):
    return hours * 3600000 + mins * 60000 + secs * 1000 + ms


def parse_whisper_line(line):
    text = line.split(']', 1)[1].strip()

    line = line.strip()
    time_segment = "".join(line.partition("]")[0:1])
    time_segment = time_segment.replace("[", "")
    start_str, end_str = time_segment.split("-->")

    s_h, s_m, s_s, s_ms = parse_whisper_time_string(start_str)
    e_h, e_m, e_s, e_ms = parse_whisper_time_string(end_str)
    start_time_ms = times_to_ms(s_h, s_m, s_s, s_ms)
    end_time_ms = times_to_ms(e_h, e_m, e_s, e_ms)
    return start_time_ms, end_time_ms, text


def format_time(seconds):
    hours = math.floor(seconds / 3600)
    seconds %= 3600
    minutes = math.floor(seconds / 60)
    seconds %= 60
    milliseconds = round((seconds - math.floor(seconds)) * 1000)
    seconds = math.floor(seconds)
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    return formatted_time


def generate_subtitle_file(segments, audio_path):
    input_video = audio_path
    input_video_name = input_video.replace(".mp4", "")

    subtitle_file = f"{input_video_name}.srt"
    text = ""
    for index, segment in enumerate(segments):
        segment_start = format_time(segment["start"])
        segment_end = format_time(segment["end"])
        text += f"{str(index+1)}\n"
        text += f"{segment_start} --> {segment_end}\n"
        text += f"{segment['text']}\n"
        text += "\n"

    f = open(subtitle_file, "w")
    f.write(text)
    f.close()


def start_live_transcription(list_with_subtitle_text_and_times, audio_path, model_version, input_language, generate_sub_file=False):
    model = whisper.load_model(model_version)
    model_compiled = intel_npu_acceleration_library.compile(
        model, dtype=torch.int8)
    result = model_compiled.transcribe(audio_path, fp16=True, language=input_language)
    segments = result["segments"]

    for segment in segments:
        segment_start_time = format_time(segment['start'])
        segment_end_time = format_time(segment['end'])
        segment_text = segment['text']
        start_time, end_time, text = parse_whisper_line(
            f"[{segment_start_time} --> {segment_end_time}] {segment_text}")
        list_with_subtitle_text_and_times.append((start_time, end_time, text))
    if generate_sub_file:
        generate_subtitle_file(segments, audio_path)
