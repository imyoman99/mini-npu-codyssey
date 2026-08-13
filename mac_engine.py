"""
mac_engine.py — MAC(Multiply-Accumulate) 연산 코어
- mac_2d  : 2차원 배열 기본 버전 (교육/비교용)
"""


def mac_2d(input_2d: list[list[float]], filter_2d: list[list[float]]) -> float:
    """2차원 배열 기반 MAC: 동일 위치 곱셈 후 누적."""
    n = len(input_2d)
    acc = 0.0
    for i in range(n):
        for j in range(n):
            acc += input_2d[i][j] * filter_2d[i][j]
    return acc

def mac_1d(input_1d: list[float], filter_1d: list[float]) -> float:
    """1차원 배열 기반 MAC (최적화 버전)"""
    acc = 0.0
    for i in range(len(input_1d)):
        acc += input_1d[i] * filter_1d[i]
    return acc