import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog


base_path = os.path.dirname(os.path.abspath(__file__))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(f'{base_path}/ui_main.ui', self)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("영수증 관리 프로그램 v1.0.0")
        self.setFixedSize(694, 49)

        # button
        self.btn_receipt_folder.clicked.connect(self.on_excel)
        self.btn_execute.clicked.connect(self.on_execute)

    def on_excel(self):
        print("on_excel called")

    def on_execute(self):
        print("on_execute called")
