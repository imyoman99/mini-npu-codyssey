"""
benchmark.py — MAC 연산 시간 측정 유틸리티
- 독립 실행/모드 아님. runner가 호출하는 계측 도구.
- 10회 반복 평균, perf_counter 사용
"""

from time import perf_counter

from mac_engine import mac_2d
from generator import generate_cross

REPEAT = 10


def measure(func, *args, repeat=REPEAT):
    """func(*args)를 repeat회 실행한 평균 시간(초)을 반환."""
    total = 0.0
    for _ in range(repeat):
        start = perf_counter()
        func(*args)
        total += perf_counter() - start
    return total / repeat


def profile_sizes(sizes):
    """각 크기별 MAC 평균 시간을 [(n, 평균초), ...]로 반환. 패턴 생성은 측정 제외."""
    rows = []
    for n in sizes:
        pattern = generate_cross(n)   # 준비 구간 — 측정 제외
        filt = generate_cross(n)
        rows.append((n, measure(mac_2d, pattern, filt)))
    return rows