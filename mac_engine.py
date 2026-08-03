"""
mac_engine.py — MAC(Multiply-Accumulate) 연산 코어
- mac_2d  : 2차원 배열 기본 버전 (교육/비교용)
- mac_1d  : 1차원 Flat 배열 최적화 버전 (실제 NPU 방식)
- flatten : 2D → 1D 변환 유틸
"""

def mac_2d(input_2d: list[list[float]], filter_2d: list[list[float]]) -> float:
    """2차원 배열 기반 MAC: 동일 위치 곱셈 후 누적."""
    n = len(input_2d)
    acc = 0.0
    for i in range(n):
        for j in range(n):
            acc += input_2d[i][j] * filter_2d[i][j]
    return acc

def flatten(matrix_2d: list[list[float]]) -> list[float]:
    """2차원 행렬을 1차원 연속 리스트로 펼친다 (Row-major)."""
    return [value for row in matrix_2d for value in row]

def mac_1d(input_flat: list[float], filter_flat: list[float]) -> float:
    """1차원 Flat 배열 기반 MAC: 인덱스 계산 오버헤드 최소화."""
    acc = 0.0
    for a, b in zip(input_flat, filter_flat):
        acc += a * b
    return acc