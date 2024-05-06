import os
import sys
import pathlib
import threading
import platform
import vlc
from PyQt6.QtGui import QAction
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QSizePolicy
from subtitles import SubtitleBox
from translate import get_languages, start_live_translation
from whisper_transcription import start_live_transcription


class Media_player(QtWidgets.QMainWindow):
    def __init__(self, settings):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle("Media Player")
        self.settings = settings
        self.instance = vlc.Instance()
        self.media = None
        self.media_player = self.instance.media_player_new()
        self.text_font = QtGui.QFont('Times', 20)
        self.generate_sub_file = self.settings['generate_sub_file']
        self.create_ui()
        self.is_paused = False

    def create_ui(self):
        self.widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.widget)

        self.video_frame = QtWidgets.QFrame()

        self.palette = self.video_frame.palette()
        self.palette.setColor(
            QtGui.QPalette.ColorRole.Window, QtGui.QColor(0, 0, 0))
        self.video_frame.setPalette(self.palette)
        self.video_frame.setAutoFillBackground(True)

        self.slider_position = QtWidgets.QSlider(
            QtCore.Qt.Orientation.Horizontal, self)
        self.slider_position.setToolTip("Position")
        self.slider_position.setMaximum(1000)
        self.slider_position.sliderMoved.connect(self.set_position)
        self.slider_position.sliderPressed.connect(self.set_position)
        self.slider_label = QtWidgets.QLabel()
        self.slider_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.progress_bar = QtWidgets.QProgressBar(self)
        opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
        opacity_effect.setOpacity(0.4)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setGraphicsEffect(opacity_effect)
        self.progress_bar.setDisabled(True)

        self.h_button_box = QtWidgets.QHBoxLayout()
        self.play_button = QtWidgets.QPushButton("Play")
        self.h_button_box.addWidget(self.play_button)
        self.play_button.clicked.connect(self.play_pause)

        self.stop_button = QtWidgets.QPushButton("Stop")
        self.h_button_box.addWidget(self.stop_button)
        self.stop_button.clicked.connect(self.stop)

        icon_resolution = QtCore.QSize(32, 32)
        self.volume_low_icon = QtWidgets.QLabel(self)
        low_pixmap = QtGui.QPixmap(".\\media\\low-volume.png")
        low_pixmap = low_pixmap.scaled(icon_resolution)
        self.volume_low_icon.setPixmap(low_pixmap)
        self.h_button_box.addWidget(self.volume_low_icon)

        self.volume_slider = QtWidgets.QSlider(
            QtCore.Qt.Orientation.Horizontal, self)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(self.media_player.audio_get_volume())
        self.volume_slider.setToolTip("Volume")
        self.h_button_box.addWidget(self.volume_slider)
        self.volume_slider.valueChanged.connect(self.set_volume)

        self.volume_high_icon = QtWidgets.QLabel(self)
        high_pixmap = QtGui.QPixmap(".\\media\\high-volume.png")
        high_pixmap = high_pixmap.scaled(icon_resolution)
        self.volume_high_icon.setPixmap(high_pixmap)
        self.h_button_box.addWidget(self.volume_high_icon)

        self.slider_layout = QtWidgets.QHBoxLayout()
        self.slider_layout.setSpacing(10)
        self.v_box_layout = QtWidgets.QVBoxLayout()
        self.video_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.v_box_layout.addWidget(self.video_frame)

        self.slider_layout.addWidget(self.slider_position)
        self.slider_position.setStyleSheet(
            "QSlider::handle { width: 10px; height: 1px;}")

        self.slider_layout.addWidget(self.slider_label)
        self.v_box_layout.addLayout(self.h_button_box)
        self.v_box_layout.addLayout(self.slider_layout)
        self.v_box_layout.setSpacing(10)

        self.subtitle_box = SubtitleBox(
            self, self.settings['in_lan'], self.settings['out_lan'])
        self.subtitle_box.setFont(self.text_font)

        self.v_box_layout.addWidget(self.subtitle_box)
        self.v_box_layout.addWidget(self.progress_bar)

        self.widget.setLayout(self.v_box_layout)

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        open_action = QAction("Load Video", self)
        close_action = QAction("Close App", self)
        file_menu.addAction(open_action)
        file_menu.addAction(close_action)
        open_action.triggered.connect(self.open_audio_file)
        close_action.triggered.connect(sys.exit)

        language_output_menu = menu_bar.addMenu("OutputLanguage")
        for lan_abbreviation, lan_full in get_languages().items():
            lan_string = f"{lan_abbreviation} ({lan_full})"
            language_output_menu.addAction(
                lan_string, self.language_output_menu_clicked)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_ui)

    def language_output_menu_clicked(self):
        action = self.sender()
        self.subtitle_box.output_language_select(action.text())
        self.start_new_translation_thread()

    def start_new_translation_thread(self):
        try:
            self.translation_thread._stop()
        except Exception as exception:
            print("start_new_translation_thread:", exception)

        self.subtitle_box.loaded_subtitles = list()
        self.progress_bar.setValue(0)

        self.translation_thread = threading.Thread(target=start_live_translation,
                                                   args=(self.subtitle_box.original_subtitles,
                                                         self.subtitle_box.loaded_subtitles,
                                                         self.subtitle_box.get_output_language()))
        self.translation_thread.start()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_BracketLeft:
            time_in_ms = self.media_duration * self.media_player.get_position()
            new_time = time_in_ms - 1000
            self.set_new_audio_position(new_time_ms=new_time)

        elif event.key() == QtCore.Qt.Key.Key_BracketRight:
            time_in_ms = self.media_duration * self.media_player.get_position()
            new_time = time_in_ms + 1000
            self.set_new_audio_position(new_time_ms=new_time)

    def set_new_audio_position(self, new_time_ms):
        new_pos = new_time_ms / self.media_duration
        if new_pos > 1:
            new_pos = 1
        if new_pos < 0:
            new_pos = 0
        self.media_player.set_position(new_pos)

    def play_pause(self):
        if self.media_player.is_playing():
            self.media_player.pause()
            self.play_button.setText("Play")
            self.is_paused = True
            self.timer.stop()
        else:
            if self.media_player.play() == -1:
                self.open_audio_file()
                return

            self.media_player.play()
            while self.media_player.get_state() != vlc.State.Playing:
                continue

            self.play_button.setText("Pause")
            self.timer.start()
            self.is_paused = False
            self.video_frame.resize(1, 1)
            while self.video_frame.size().width() == 1:
                self.resize_1_percent()

    def stop(self):
        self.media_player.stop()
        self.play_button.setText("Play")

    def open_audio_file(self):
        dialog_txt = "Choose Media File"
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self, dialog_txt, os.path.expanduser('~'))
        if not filename or not os.path.exists(filename[0]):
            return

        self.media = self.instance.media_new(filename[0])
        self.subtitle_box.original_subtitles = None
        self.media_player.set_media(self.media)

        self.media.parse()

        self.setWindowTitle(self.media.get_meta(0))

        while self.media.get_duration() < 0:
            continue
        self.media_duration = self.media.get_duration()

        if platform.system() == "Linux":
            self.media_player.set_xwindow(int(self.video_frame.winId()))
        elif platform.system() == "Windows":
            self.media_player.set_hwnd(int(self.video_frame.winId()))

        audio_file_path = pathlib.Path(filename[0])
        self.audio_file_path = audio_file_path
        subtitle_path = audio_file_path.with_suffix(".srt")
        if os.path.exists(subtitle_path):
            print("Loading subtitles at", subtitle_path)
            self.subtitle_box.loaded_subtitles = list()
            self.subtitle_box.load_subtitles(subtitle_path)
        else:
            print("Automatically transcribing subtitles")
            self.start_new_transcription_thread()

    def resize_1_percent(self):
        current_size = self.size()
        new_width = int(current_size.width() * 1.01)
        new_height = int(current_size.height() * 1.01)
        self.resize(new_width, new_height)
        self.resize(current_size.width(), current_size.height())

    def start_new_transcription_thread(self):
        try:
            self.transcription_thread._stop()
        except Exception as exception:
            print("start_new_transcription_thread:", exception)

        try:
            print(self.audio_file_path)
        except AttributeError:
            return

        self.subtitle_box.loaded_subtitles = list()
        self.progress_bar.setValue(0)

        self.transcription_thread = threading.Thread(target=start_live_transcription,
                                                     args=(self.subtitle_box.loaded_subtitles,
                                                           str(self.audio_file_path),
                                                           self.settings['model'],
                                                           self.settings['in_lan'],
                                                           self.generate_sub_file))
        self.transcription_thread.start()

    def set_volume(self, volume):
        self.media_player.audio_set_volume(volume)

    def set_position(self):
        self.timer.stop()
        pos = self.slider_position.value()
        self.media_player.set_position(pos / 1000.0)
        self.timer.start()

    def update_ui(self):
        media_pos = int(self.media_player.get_position()*100)
        self.slider_position.setValue(media_pos*10)
        try:
            time_in_ms = self.media_duration * self.media_player.get_position()
            elapsed_time = QtCore.QTime(0, 0).addSecs(int(time_in_ms/1000))
            self.slider_label.setText(elapsed_time.toString("hh:mm:ss"))
            self.subtitle_box.update_subtitles(time_in_ms)
            if len(self.subtitle_box.loaded_subtitles) > 0:
                if self.subtitle_box.original_subtitles == None:
                    self.subtitle_box.original_subtitles = self.subtitle_box.loaded_subtitles
                last_caption = self.subtitle_box.loaded_subtitles[-1]
                last_time = last_caption[1]
                if self.media_duration > 0:
                    if last_time > (4/5)*self.media_duration:
                        last_time = self.media_duration
                    relative_transcription_progress = round(
                        (last_time / self.media_duration)*100)
                    self.progress_bar.setValue(
                        relative_transcription_progress)
        except AttributeError as error:
            print("AttributeError, update UI: ", error)

        if not self.media_player.is_playing():
            self.timer.stop()
            if not self.is_paused:
                self.stop()
