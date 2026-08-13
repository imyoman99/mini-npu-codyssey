"""
benchmark.py — MAC 연산 시간 측정 유틸리티
"""
from time import perf_counter

from mac_engine import mac_2d, mac_1d

REPEAT = 10


def measure(func, *args, repeat=REPEAT):
    total = 0.0
    for _ in range(repeat):
        start = perf_counter()
        func(*args)
        total += perf_counter() - start
    return total / repeat


def profile_sizes(sizes):
    """각 크기별 2D 및 1D MAC 평균 시간을 [(n, 2D초, 1D초), ...]로 반환."""
    rows = []
    for n in sizes:
        # 1. 원본 2차원 배열 생성
        pattern_2d = [[1.0 if (i == n // 2 or j == n // 2) else 0.0 for j in range(n)] for i in range(n)]
        filt_2d = [[1.0 if (i == n // 2 or j == n // 2) else 0.0 for j in range(n)] for i in range(n)]
        
        # 2. 1차원 배열(길이 N²)로 변환하여 메모리 접근 패턴 단순화 (보너스 과제)
        pattern_1d = [val for row in pattern_2d for val in row]
        filt_1d = [val for row in filt_2d for val in row]
        
        # 3. 동일 입력, 동일 반복 횟수로 시간 측정
        time_2d = measure(mac_2d, pattern_2d, filt_2d)
        time_1d = measure(mac_1d, pattern_1d, filt_1d)
        
        rows.append((n, time_2d, time_1d))
    return rows