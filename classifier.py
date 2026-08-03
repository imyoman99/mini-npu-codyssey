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
    diff = score_cross - score_x
    if abs(diff) < EPSILON:
        return 'UNDECIDED'
    return label_cross if diff > 0 else label_x