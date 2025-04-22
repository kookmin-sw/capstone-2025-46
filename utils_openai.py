import time

from openai import OpenAI
import logging_config
import utils


utils.init_settings()
client = OpenAI(
    # This is the default and can be omitted
    api_key=utils.settings["openai_api_key"],
)


def extract_user_info(text):
    start_time = time.perf_counter()
    prompt = (f"전달하는 내용은 영수증을 OCR로 추출한 텍스트야. 카드번호, 승인일자, 금액, 가맹점명 등의 가능한 많은 정보를 정확하게 추출해서 json으로 리턴해줘."
              f"json 포맷이 영수증마다 변경되면 안되니깐 아래 예시를 참고해서 만들어줘."
              f"예시) ") + "{'receipt': {'merchant_name': '한국철도공사', 'merchant_id': '314-82-10024', 'address': '대전광역시 동구 중앙로 240', 'card_number': '52758500****799*', 'approval_date': '2025-01-09', 'amount': 44000, 'transaction_type': '일시불 신용카드 결제', 'issue_date': '2025-01-10', 'issue_time': '2025-01-13 09:38', 'representative_phone': '1588-7788', 'train_info': {'train_type': 'KTX-산천', 'train_number': '4052', 'departure': '순천', 'departure_time': '15:50', 'arrival': '용산', 'arrival_time': '18:34'}, 'passenger_info': {'adult_count': 1, 'child_count': 0, 'discount': 0}, 'receipt_number': '82126-0110-17435-23', 'note': '본 영수증은 세금계산서로 사용하실 수 없습니다. 고속철도는 부가가치세가 포함되어 있습니다.'}}"

    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",  # 적절한 모델명으로 변경
        messages=[
            {"role": "system", "content": f"{prompt}"},
            {"role": "user",
             "content": f"{text[:3000]}"},
        ],
        temperature=0.1,
        max_tokens=500,
    )

    elapsed_time = time.perf_counter() - start_time
    logging_config.logger.info(f"openai reply 생성 처리 시간: {elapsed_time}초")

    # return chat_completion.choices[0].text
    return chat_completion.choices[0].message.content
