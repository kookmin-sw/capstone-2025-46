import os
import json
import time
import uuid
import logging_config
import requests
import utils
import utils_openai


def call_ncp_ocr(image_binary, image_format):
    """주어진 이미지 이진 데이터와 포맷(jpg, png 등)을 이용해 NCP OCR API 호출"""
    request_json = {
        'images': [
            {
                'format': image_format,
                'name': 'demo'
            }
        ],
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }
    payload = {'message': json.dumps(request_json).encode('UTF-8')}
    files = [
        ('file', ('image.' + image_format, image_binary, 'application/octet-stream'))
    ]
    headers = {
        'X-OCR-SECRET': utils.settings['secret_key'],
    }

    response = requests.post(utils.settings['api_url'], headers=headers, data=payload, files=files)
    try:
        result_json = response.json()
    except Exception as e:
        logging_config.logger.error("OCR API 응답 JSON 파싱 실패: %s", e)
        return None
    logging_config.logger.debug("전체 응답:")
    # logging_config.logger.debug(json.dumps(result_json, indent=4, ensure_ascii=False))

    # 모든 이미지의 모든 필드에서 "inferText"를 이어붙임
    concatenated_text = ""
    for image in result_json.get("images", []):
        for field in image.get("fields", []):
            text = field.get("inferText")
            if text:
                concatenated_text += text + " "
    concatenated_text = concatenated_text.strip()

    logging_config.logger.debug("\n이어 붙인 텍스트 결과:")
    logging_config.logger.debug(concatenated_text)

    # ChatGPT 처리를 위한 사용자 정보 추출
    extracted_text = utils_openai.extract_user_info(concatenated_text)
    # logging_config.logger.debug(extracted_text)

    # 1. 앞뒤의 ```json, ``` 태그 제거
    if extracted_text.startswith("```json"):
        extracted_text = extracted_text[len("```json"):].strip()
    if extracted_text.endswith("```"):
        extracted_text = extracted_text[:-3].strip()

    # 2. JSON 파싱 시도
    try:
        data = json.loads(extracted_text)
        logging_config.logger.debug(data)
    except json.JSONDecodeError as e:
        logging_config.logger.debug("JSON 파싱 오류: %s", e)
        data = None

    return data


def process_image_file(file_path):
    """이미지 파일(jpg, png 등)에 대해 OCR 처리"""
    ext = os.path.splitext(file_path)[1].lower().lstrip('.')
    if ext not in ['jpg', 'jpeg', 'png']:
        logging_config.logger.debug("지원하지 않는 이미지 포맷: %s", file_path)
        return None

    with open(file_path, 'rb') as f:
        image_binary = f.read()
    logging_config.logger.debug("파일 처리 시작: %s", file_path)
    return call_ncp_ocr(image_binary, ext)


def process_ocr(file_path):
    """ocr_test 폴더 내의 모든 파일을 처리"""
    result = process_image_file(file_path)
    logging_config.logger.debug("결과 [%s]: %s", file_path, result)
    return result


# def process_ocr_test_folder(folder_path):
#     """ocr_test 폴더 내의 모든 파일을 처리"""
#     results = []
#     for file_name in os.listdir(folder_path):
#         file_path = os.path.join(folder_path, file_name)
#         if os.path.isfile(file_path):
#             ext = os.path.splitext(file_name)[1].lower()
#             if ext in ['.jpg', '.jpeg', '.png']:
#                 result = process_image_file(file_path)
#                 logging_config.logger.debug("결과 [%s]: %s", file_name, result)
#                 results.append(f"{file_name} : {result}")
#             else:
#                 logging_config.logger.debug("지원하지 않는 파일 포맷: %s", file_name)
#
#     for info in results:
#         logging_config.logger.debug(info)


# if __name__ == "__main__":
#     utils.init_settings()
#     folder = "requests"
#     process_ocr_test_folder(folder)
