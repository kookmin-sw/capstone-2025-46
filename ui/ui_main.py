import logging_config
import utils
import os
from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QHeaderView, QAbstractItemView

from worker import Worker

base_path = os.path.dirname(os.path.abspath(__file__))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(f'{base_path}/ui_main.ui', self)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("영수증 관리 프로그램 v1.0.0")
        self.setFixedSize(694, 345)

        self.worker_thread = Worker(self)
        self.worker_thread.start()

        # button
        self.btn_receipt_folder.clicked.connect(self.on_excel)
        self.btn_execute.clicked.connect(self.on_execute)

        header = self.tv_receipt.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.tv_receipt.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tv_receipt_result.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.init_data_setting()

    def init_data_setting(self):
        self.txt_receipt_folder.setText(utils.settings["init_excel_filepath"])
        if self.txt_receipt_folder.text() != "":
            self.set_table_data()

    def on_excel(self):
        print("on_excel called")
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly  # 디렉토리만 표시
        options &= ~QFileDialog.DontUseNativeDialog  # 네이티브 스타일 강제 사용

        # 폴더 선택 다이얼로그 열기
        folder_path = QFileDialog.getExistingDirectory(
            parent=self,
            caption="Select a Folder",  # 다이얼로그 제목
            directory="",  # 초기 디렉토리
            options=options  # 옵션 설정
        )
        if folder_path:
            self.txt_receipt_folder.setText(folder_path)
            self.set_table_data()

    def set_table_data(self):
        # 폴더 경로를 가져옵니다.
        folder_path = self.txt_receipt_folder.text()

        # 폴더 경로가 비어 있거나 존재하지 않으면 종료
        if not folder_path or not os.path.isdir(folder_path):
            print("유효한 폴더 경로가 없습니다.")
            return

        # 폴더 내 파일 목록 가져오기
        files = os.listdir(folder_path)

        # QTableView에 데이터를 설정할 모델 생성
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['파일명'])  # "파일명" 컬럼 헤더 설정

        # 폴더 내 파일 이름을 테이블에 추가
        for file_name in files:
            # 파일명만 추가
            item = QStandardItem(file_name)
            model.appendRow([item])

        # QTableView에 모델 설정
        self.tv_receipt.setModel(model)

    def on_execute(self):
        logging_config.logger.debug("on_execute called")
