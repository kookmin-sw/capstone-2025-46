import time
import pandas as pd
import shutil
import sys
from datetime import datetime

import logging_config
import utils
import os
import models
from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QHeaderView, QAbstractItemView, QMessageBox
import win32com.client as win32

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
            ai_result.get('note', ''),
            ai_result.get('usage_purpose', '')
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
        df = df[['승인일', '상호', '금액', '카드 번호', '사용 용도']]
        df['카드 번호'] = df['카드 번호'].apply(lambda x: x[-4:])
        df['증빙유무'] = '유'

        # 승인일 기준으로 오름차순 정렬
        df = df.sort_values(by='승인일', ascending=True).reset_index(drop=True)

        # 2. 파일 경로 및 복사
        folder_path = self.txt_receipt_folder.text()
        today_str = datetime.today().strftime("%Y%m%d")
        template_path = os.path.join(root_path, "법인카드 사용내역.xlsx")
        output_path = os.path.join("C:\\Users\\cjdtn\\OneDrive", f"법인카드 사용내역_작성본_{today_str}.xlsx")

        shutil.copyfile(template_path, output_path)
        time.sleep(2)

        # 3. Excel 열기
        excel = win32.gencache.EnsureDispatch('Excel.Application')
        excel.Visible = False
        wb = excel.Workbooks.Open(output_path, ReadOnly=False)

        # 4. 데이터 시트 처리 (Sheet1)
        ws1 = wb.Sheets(1)

        today = datetime.today()
        date_title = f"{today.year}년 {today.month}월 법인카드(출장용) 사용내역서(이윤로)"
        ws1.Cells(1, 1).Value = date_title

        start_row = 6
        for i, row in df.iterrows():
            ws1.Cells(start_row + i, 3).Value = row['카드 번호']  # C열
            ws1.Cells(start_row + i, 4).Value = row['승인일']  # D열
            ws1.Cells(start_row + i, 5).Value = row['상호']  # E열
            ws1.Cells(start_row + i, 6).Value = row['사용 용도']  # F열
            ws1.Cells(start_row + i, 7).Value = row['금액']  # G열
            ws1.Cells(start_row + i, 10).Value = row['증빙유무']  # J열

        # 5. 이미지 삽입 (Sheet2)
        try:
            ws2 = wb.Sheets("영수증 첨부")
        except Exception:
            ws2 = wb.Sheets.Add(After=wb.Sheets(wb.Sheets.Count))
            ws2.Name = "영수증 첨부"

        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.jpg')]
        top = 10  # Y축 시작 위치
        for image_file in image_files:
            image_path = os.path.normpath(os.path.abspath(os.path.join(folder_path, image_file)))
            if os.path.exists(image_path):
                # AddPicture(경로, 링크?, 저장?, 좌측위치, 상단위치, 너비, 높이)
                shape = ws2.Shapes.AddPicture(
                    Filename=image_path,
                    LinkToFile=False,
                    SaveWithDocument=True,
                    Left=10,  # X 위치 (A열 근처)
                    Top=top,  # Y 위치
                    Width=-1,  # 원본 크기 유지
                    Height=-1
                )
                top += shape.Height + 20  # 다음 이미지 아래로 내리기 (조정 가능)

        # 6. 저장 및 종료
        wb.Save()
        wb.Close()
        excel.Quit()

        done_folder = os.path.join(root_path, "done")
        for image_file in image_files:
            image_path = os.path.join(folder_path, image_file)
            done_file_path = os.path.join(done_folder, image_file)
            shutil.move(image_path, done_file_path)
