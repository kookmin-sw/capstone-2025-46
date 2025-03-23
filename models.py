from typing import Optional

# 철도 영수증에서 추출 가능한 항목 정의
header = [
    "상호", "상호 ID", "주소", "카드 번호", "승인일", "금액", "거래 종류", "발행일",
    "발행 시간", "대표 전화", "열차 종류", "열차 번호", "출발지", "출발 시간",
    "도착지", "도착 시간", "성인 수", "어린이 수", "할인", "영수증 번호", "비고"
]


class AiResult:
    merchant_name: Optional[str]
    merchant_id: Optional[str]
    address: Optional[str]
    card_number: Optional[str]
    approval_date: Optional[str]
    amount: Optional[int]
    transaction_type: Optional[str]
    issue_date: Optional[str]
    issue_time: Optional[str]
    representative_phone: Optional[str]
    train_type: Optional[str]
    train_number: Optional[str]
    departure: Optional[str]
    departure_time: Optional[str]
    arrival: Optional[str]
    arrival_time: Optional[str]
    adult_count: Optional[int]
    child_count: Optional[int]
    discount: Optional[int]
    receipt_number: Optional[str]
    note: Optional[str]
