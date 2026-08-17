"""
classifier.py — Epsilon 기반 판정 로직
부동소수점 오차를 인정하고, 허용오차(EPSILON) 이내의 차이는
'UNDECIDED'로 판정하여 오판을 원천 차단한다.
"""

EPSILON = 1e-9  # 부동소수점 오차 방어선 (정책으로 명문화)


def classify(score_cross, score_x, label_cross='Cross', label_x='X'):
    """
    두 MAC 점수를 비교해 패턴을 판정한다.
    - |차이| < EPSILON → 'UNDECIDED' (동점/오차 범위)
    - cross 우세      → label_cross
    - x 우세          → label_x
    """
    diff = score_cross - score_x  # Cross 점수에서 X 점수를 빼서 점수 차이 계산
    if abs(diff) < EPSILON:
        return 'UNDECIDED'  # 점수 차이가 허용 오차(EPSILON)보다 작으면 동점(UNDECIDED) 판정
    return label_cross if diff > 0 else label_x  # Cross 점수가 더 높으면 Cross 라벨, X 점수가 더 높으면 X 라벨 반환