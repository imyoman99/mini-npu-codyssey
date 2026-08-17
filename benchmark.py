"""
benchmark.py — MAC 연산 시간 측정 유틸리티
"""
from time import perf_counter
from mac_engine import mac_2d, mac_1d
from pattern_generator import generate_patterns


REPEAT = 10  # 함수 실행 시간을 측정할 때 반복할 횟수 상수 정의 (기본 10번)


def measure(func, *args, repeat=REPEAT):
    total = 0.0  # 측정한 모든 실행 시간을 합산할 변수 초기화
    for _ in range(repeat):  # 지정된 횟수(REPEAT)만큼 성능 측정 반복
        start = perf_counter()  # 현재 시각(고정밀 타이머) 기록
        func(*args)  # 측정하고자 하는 함수를 전달받은 인자(*args)와 함께 실행
        total += perf_counter() - start  # (끝난 시각 - 시작 시각)을 계산해 총 시간에 누적
    return total / repeat  # 총 소요 시간을 반복 횟수로 나누어 '평균 실행 시간' 반환


def profile_sizes(sizes):
    """각 크기별 2D 및 1D MAC 평균 시간을 [(n, 2D초, 1D초), ...]로 반환."""
    rows = []
    for n in sizes:
        # 중복 로직 제거하고 생성기 재사용!
        cross_pat, _ = generate_patterns(n)
        
        # 1. 원본 2차원 배열 생성 (Cross 패턴을 입력과 필터로 동일하게 세팅)
        pattern_2d = cross_pat
        filt_2d = cross_pat
        
        # 2. 1차원 배열(길이 N²)로 변환
        pattern_1d = [val for row in pattern_2d for val in row]
        filt_1d = [val for row in filt_2d for val in row]
        
        # 3. 동일 입력, 동일 반복 횟수로 시간 측정
        time_2d = measure(mac_2d, pattern_2d, filt_2d)
        time_1d = measure(mac_1d, pattern_1d, filt_1d)
        
        rows.append((n, time_2d, time_1d))
        
    return rows