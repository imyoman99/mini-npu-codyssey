"""
normalizer.py — 라벨 정규화 계층
파편화된 표기('+', 'cross', 'x', '엑스' 등)를 표준 라벨로 통일한다.
데이터의 '입구'에서 통제하는 방어적 프로그래밍의 1차 방어선.
"""

LABEL_MAP = {
    # CROSS 계열
    '+': 'Cross',
    'cross': 'Cross',
    'plus': 'Cross',
    '십자': 'Cross',
    '십자가': 'Cross',
    
    # X 계열
    'x': 'X',
    'ex': 'X',
    '엑스': 'X',
}

def normalize_label(raw):
    """원시 라벨 → 표준 라벨('Cross'/'X'). 매핑 불가 시 None 반환."""
    if raw is None:
        return None  # 라벨 값이 아예 없으면 None 반환
    
    key = str(raw).strip().lower()  # 입력된 라벨을 문자열로 바꾸고, 앞뒤 공백을 없앤 뒤 소문자로 변환
    return LABEL_MAP.get(key)  # 변환된 키를 이용해 표준 라벨 맵에서 값을 찾아 반환 (없으면 None)