import datetime
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from os import mkdir

if not os.path.exists("logs"):
    mkdir("logs")

logger = logging.getLogger("log")
logger.setLevel(logging.DEBUG)
logger.handlers.clear()

# 현재 날짜로 파일 이름 지정
today = datetime.datetime.now().strftime('%m%d')  # 'YYYYMMDD' 형식
log_filename = f'logs/log_{today}.txt'

rh = RotatingFileHandler(
    log_filename, maxBytes=5 * 1024 * 1024, backupCount=20, encoding="utf-8"
)
rh.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(message)s")
rh.setFormatter(formatter)

ch = logging.StreamHandler(stream=sys.stdout)
ch.setFormatter(formatter)

logger.addHandler(rh)
logger.addHandler(ch)
