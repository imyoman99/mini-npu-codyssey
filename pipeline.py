"""
pipeline.py — 분석 파이프라인 코어
패턴 하나를 받아 MAC → 판정까지 수행하는 순수 로직.
입출력(콘솔/JSON)을 전혀 모른다 → 어디서든 재사용 가능.
"""

from mac_engine import mac_2d
from classifier import classify


def analyze(pattern_2d):
    """패턴 → (cross점수, x점수, 판정). 파이프라인의 공통 코어."""
    n = len(pattern_2d)
    cross_filter = [[1.0 if (i == n // 2 or j == n // 2) else 0.0 for j in range(n)] for i in range(n)]
    x_filter = [[1.0 if (i == j or i + j == n - 1) else 0.0 for j in range(n)] for i in range(n)]
    score_cross = mac_2d(pattern_2d, cross_filter)
    score_x = mac_2d(pattern_2d, x_filter)
    return score_cross, score_x, classify(score_cross, score_x)


def validate_schema(case):
    """JSON 케이스 스키마 사전 검증. 문제 시 ValueError."""
    if 'input' not in case and 'pattern' not in case:
        raise ValueError("'input' 또는 'pattern' 필드 누락")

    pattern = case.get('input', case.get('pattern'))
    n = len(pattern)
    if n < 3:
        raise ValueError(f"패턴 크기가 3 미만: {n}")
    for row in pattern:
        if len(row) != n:
            raise ValueError(f"행 길이 불일치: {len(row)} != {n}")