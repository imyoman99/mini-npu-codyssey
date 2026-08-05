"""
benchmark.py — MAC 연산 시간 측정 유틸리티
"""
from time import perf_counter

from mac_engine import mac_2d

REPEAT = 10


def measure(func, *args, repeat=REPEAT):
    total = 0.0
    for _ in range(repeat):
        start = perf_counter()
        func(*args)
        total += perf_counter() - start
    return total / repeat


def profile_sizes(sizes):
    """각 크기별 2D MAC 평균 시간을 [(n, 2D초), ...]로 반환."""
    rows = []
    for n in sizes:
        pattern = [[1.0 if (i == n // 2 or j == n // 2) else 0.0 for j in range(n)] for i in range(n)]
        filt = [[1.0 if (i == n // 2 or j == n // 2) else 0.0 for j in range(n)] for i in range(n)]
        time_2d = measure(mac_2d, pattern, filt)
        rows.append((n, time_2d))
    return rows