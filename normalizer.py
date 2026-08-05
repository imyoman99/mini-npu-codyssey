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
        return None
    key = str(raw).strip().lower()
    return LABEL_MAP.get(key)