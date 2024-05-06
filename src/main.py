
import sys
from PyQt6 import QtWidgets
from player import Player

SETTINGS = {
    "in_lan" : "en",
    "out_lan" : "en",
    "model":"small",
    "font_size":20,
    "time_change_ms":1000,
    "generate_sub_file":False
}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    player = Player(SETTINGS)
    player.show()
    player.resize(640, 480)
    sys.exit(app.exec())