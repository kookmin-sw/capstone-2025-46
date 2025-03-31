import sys
from PyQt5 import QtWidgets
import utils
from ui.ui_main import MainWindow


if __name__ == '__main__':
    utils.init_settings()
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
