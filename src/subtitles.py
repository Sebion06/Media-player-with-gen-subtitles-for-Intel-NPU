from PyQt6 import QtWidgets
from whisper_transcription import parse_whisper_time_string, times_to_ms


def parse_srt_time_string(srt_time):
    # srt_time: <str>, ex: "00:00:00,000 --> 00:00:21,000"
    start_time = srt_time.partition(' ')[0]
    end_time = srt_time.rpartition(' ')[2]
    s_h, s_m, s_s, s_ms = parse_whisper_time_string(start_time)
    e_h, e_m, e_s, e_ms = parse_whisper_time_string(end_time)
    start_time_ms = times_to_ms(s_h, s_m, s_s, s_ms)
    end_time_ms = times_to_ms(e_h, e_m, e_s, e_ms)
    return start_time_ms, end_time_ms


def load_srt_file(srt_path):
    all_info = list()

    with open(srt_path, "r", encoding='utf-8') as srt_file:
        full_file_string = srt_file.read()

    for section in full_file_string.split("\n\n"):
        section_lines = section.split("\n")

        if len(section_lines) == 3:
            number = section_lines[0]
            time_string = section_lines[1]
            text = section_lines[2]
            start, end = parse_srt_time_string(time_string)
            all_info.append((start, end, text))

    return all_info


def find_text_and_index_at_time(loaded_subtitles, time, start_index=0):
    if start_index < 0:
        start_index = 0

    active_index = start_index
    for start_time, end_time, text in loaded_subtitles[start_index:]:
        if end_time > time >= start_time:
            return text, active_index
        active_index += 1

    return None, None


class SubtitleBox(QtWidgets.QTextEdit):
    def __init__(self, player, input_language, output_language):
        super().__init__()
        self.setReadOnly(True)
        self.setMaximumHeight(60)
        self.setText("Select a video file..")

        self.word_adjust_x = -25
        self.word_adjust_y = -25

        self.player = player
        self.input_language = input_language
        self.output_language = output_language
        self.loaded_subtitles = None
        self.original_subtitles = None
        self.subtitle_index = -1

    def output_language_select(self, action_text):
        abbreviation, full_text = action_text.split(" ", 1)
        self.output_language = abbreviation

    def load_subtitles(self, pathlib_to_srt_file):
        print("loading subtitles")
        self.subtitle_index = -1
        self.loaded_subtitles = load_srt_file(pathlib_to_srt_file)

    def update_subtitles(self, time_in_ms):
        if self.loaded_subtitles is not None:

            subtitle_text, subtitle_index = find_text_and_index_at_time(loaded_subtitles=self.loaded_subtitles,
                                                                        time=time_in_ms, start_index=self.subtitle_index)
            if subtitle_text is None and subtitle_index is None:
                # restart looking cause it hasnt been found from the starting point used
                self.subtitle_index = -1
                self.setText("")
                self.update()
            elif self.subtitle_index != subtitle_index:
                self.subtitle_index = subtitle_index
                self.setText(subtitle_text)
                self.update()

    def get_output_language(self):
        return self.output_language
