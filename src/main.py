
import sys
import argparse
from PyQt6 import QtWidgets
from media_player import Media_player
from translate import get_languages


def parse_arguments():
    languages = list(get_languages().keys())
    parser = argparse.ArgumentParser(
        description='A python vlc player that transcribes subtitles on the Intel NPU, while watching a video')
    parser.add_argument('--model', dest='model', action='store', default="tiny",
                        help='Whisper-AI model version', choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument('--in_lan', dest='in_lan', action='store', default="en",
                        help='Input lanuage of media file', choices=languages)
    parser.add_argument('--out_lan', dest='out_lan', action='store', default="en",
                        help='Output language for subtitles', choices=languages)
    parser.add_argument('--gen_sub_file', dest='generate_sub_file',
                        action='store_true', default=False)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_arguments()
    app = QtWidgets.QApplication(sys.argv)
    player = Media_player(vars(args))
    player.show()
    player.resize(640, 480)
    sys.exit(app.exec())
