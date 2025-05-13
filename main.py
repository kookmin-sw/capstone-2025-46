import sys
from PyQt5 import QtWidgets
import utils
from ui.ui_main import MainWindow

# pyinstaller --add-data "C:/Users/cjdtn/PycharmProjects/capstone-2025-46/ui;ui" -F main.py

if __name__ == '__main__':
    utils.init_settings()
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
