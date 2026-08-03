"""
benchmark.py — MAC 연산 시간 측정 유틸리티
"""
from time import perf_counter

from mac_engine import mac_2d, mac_1d, flatten # 1D 함수 추가 임포트
from generator import generate_cross

REPEAT = 10

def measure(func, *args, repeat=REPEAT):
    total = 0.0
    for _ in range(repeat):
        start = perf_counter()
        func(*args)
        total += perf_counter() - start
    return total / repeat

def profile_sizes(sizes):
    """각 크기별 MAC 평균 시간을 [(n, 2D초, 1D초), ...]로 반환."""
    rows = []
    for n in sizes:
        # 패턴 생성 (측정 제외)
        pattern_2d = generate_cross(n)
        filt_2d = generate_cross(n)
        
        # 1D Flatten 변환 (측정 제외)
        pattern_1d = flatten(pattern_2d)
        filt_1d = flatten(filt_2d)

        # 최적화 전/후 비교 측정
        time_2d = measure(mac_2d, pattern_2d, filt_2d)
        time_1d = measure(mac_1d, pattern_1d, filt_1d)
        
        rows.append((n, time_2d, time_1d)) # 1D 시간 추가 반환
    return rows