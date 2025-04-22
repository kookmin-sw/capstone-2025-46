import shutil
import os
import sys
from PyQt5.QtCore import QThread, pyqtSignal
import logging_config
import queue
import utils_ncp_clova

# PyInstaller로 빌드된 경우와 아닐 경우를 구분
if getattr(sys, 'frozen', False):
    # frozen 속성이 있으면 exe로 빌드된 상태이므로, sys.executable 사용
    base_path = os.path.dirname(sys.executable)
else:
    # 그렇지 않으면 __file__을 기준으로 경로 설정
    base_path = os.path.dirname(os.path.abspath(__file__))
root_path = base_path.replace("ui", "")


class Worker(QThread):
    update_ui = pyqtSignal(str)
    update_row_by_url_signal = pyqtSignal(dict)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.commands = queue.Queue()

    def run(self):
        while True:
            command = self.commands.get()
            logging_config.logger.info(f"command: {command}")
            if command == "on_work":
                self.on_work()

    def add_command(self, command):
        self.commands.put(command)

    def on_work(self):
        logging_config.logger.debug("on_work worker start")
        folder_path = self.parent.txt_receipt_folder.text()
        if folder_path:
            done_folder = os.path.join(root_path, "done")

            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file_name)[1].lower()
                    if ext in ['.jpg', '.jpeg', '.png']:
                        ai_result = utils_ncp_clova.process_ocr(file_path)
                        self.update_row_by_url_signal.emit(ai_result.get("receipt"))
                    else:
                        logging_config.logger.debug("지원하지 않는 파일 포맷: %s", file_name)
        else:
            self.update_ui.emit(f"영수증 폴더를 선택해야 합니다.")
