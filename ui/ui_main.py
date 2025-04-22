import pandas as pd
import shutil
import sys

import logging_config
import utils
import os
import models
from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QHeaderView, QAbstractItemView, QMessageBox

from worker import Worker

base_path = os.path.dirname(os.path.abspath(__file__))
if getattr(sys, 'frozen', False):
    # frozen 속성이 있으면 exe로 빌드된 상태이므로, sys.executable 사용
    project_path = os.path.dirname(sys.executable)
else:
    # 그렇지 않으면 __file__을 기준으로 경로 설정
    project_path = os.path.dirname(os.path.abspath(__file__))
root_path = project_path.replace("ui", "")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(f'{base_path}/ui_main.ui', self)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("영수증 관리 프로그램 v1.0.0")
        self.setFixedSize(694, 345)

        self.worker_thread = Worker(self)
        self.worker_thread.update_ui.connect(self.update_log)
        self.worker_thread.update_row_by_url_signal.connect(self.update_row_by_url)  # URL 업데이트 연결
        self.worker_thread.start()

        # button
        self.btn_receipt_folder.clicked.connect(self.on_excel)
        self.btn_execute.clicked.connect(self.on_execute)
        self.btn_save.clicked.connect(self.on_save)

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
        self.worker_thread.add_command("on_work")

    def update_log(self, message):
        logging_config.logger.debug(f"update_log called - {message}")
        QMessageBox.warning(self, "경고", message)

    def update_row_by_url(self, ai_result: dict):
        # QTableView 모델 가져오기
        model = self.tv_receipt_result.model()

        # 모델이 없으면 새로 생성
        if model is None:
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(models.header)
            self.tv_receipt_result.setModel(model)

        # AiResult의 딕셔너리에서 값을 가져와서 테이블에 추가
        row_data = [
            ai_result.get('merchant_name', ''),
            ai_result.get('merchant_id', ''),
            ai_result.get('address', ''),
            ai_result.get('card_number', ''),
            ai_result.get('approval_date', ''),
            ai_result.get('amount', ''),
            ai_result.get('transaction_type', ''),
            ai_result.get('issue_date', ''),
            ai_result.get('issue_time', ''),
            ai_result.get('representative_phone', ''),
            ai_result.get('train_type', ''),
            ai_result.get('train_number', ''),
            ai_result.get('departure', ''),
            ai_result.get('departure_time', ''),
            ai_result.get('arrival', ''),
            ai_result.get('arrival_time', ''),
            ai_result.get('adult_count', ''),
            ai_result.get('child_count', ''),
            ai_result.get('discount', ''),
            ai_result.get('receipt_number', ''),
            ai_result.get('note', '')
        ]

        # 모델에 새로운 행 추가
        row_position = model.rowCount()
        model.insertRow(row_position)

        # 데이터 채우기
        for col, value in enumerate(row_data):
            item = QStandardItem(str(value))  # 값이 None이면 빈 문자열을 대입
            model.setItem(row_position, col, item)

        # QTableView 업데이트
        self.tv_receipt_result.setModel(model)
        self.tv_receipt_result.viewport().update()

    def on_save(self):
        # QTableView에서 모델을 가져옵니다.
        model = self.tv_receipt_result.model()

        # 모델에서 데이터를 DataFrame으로 변환
        data = []
        for row in range(model.rowCount()):
            row_data = []
            for column in range(model.columnCount()):
                index = model.index(row, column)
                row_data.append(index.data())
            data.append(row_data)

        # DataFrame 생성
        df = pd.DataFrame(data, columns=models.header)
        df = df[['승인일', '상호', '금액', '카드 번호']]
        df['카드 번호'] = df['카드 번호'].apply(lambda x: x[-4:])
        df['증빙유무'] = '유'

        # 모델에서 헤더 정보를 가져옵니다.
        # headers = [model.headerData(i, Qt.Horizontal) for i in range(model.columnCount())]
        # df.columns = headers  # DataFrame에 헤더를 설정

        # 저장할 파일 경로 선택 (파일 다이얼로그)
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'Excel Files (*.xlsx)')
        if file_name:
            with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
                # 첫 번째 시트에 데이터 저장
                df.to_excel(writer, index=False, header=True, sheet_name='Sheet1')

                # 워크북과 워크시트 객체 얻기
                workbook = writer.book
                worksheet1 = writer.sheets['Sheet1']

                # request 폴더에서 이미지 파일 리스트 가져오기
                folder_path = self.txt_receipt_folder.text()
                image_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.jpg')]

                # 두 번째 시트에 이미지 추가
                worksheet2 = workbook.add_worksheet('Sheet2')

                done_folder = os.path.join(root_path, "done")
                # 이미지 삽입 (여러 이미지를 순차적으로 삽입)
                row = 0  # 첫 번째 행부터 시작
                for image_file in image_files:
                    image_path = os.path.join(folder_path, image_file)
                    worksheet2.insert_image(row, 0, image_path)
                    row += 40  # 각 이미지를 15행씩 간격을 두고 삽입 (적절히 조정)

                # Excel 파일 저장
                workbook.close()

            for image_file in image_files:
                image_path = os.path.join(folder_path, image_file)
                done_file_path = os.path.join(done_folder, image_file)
                shutil.move(image_path, done_file_path)
