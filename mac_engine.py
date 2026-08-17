"""
mac_engine.py — MAC(Multiply-Accumulate) 연산 코어
- mac_2d  : 2차원 배열 기본 버전 (교육/비교용)
"""


def mac_2d(input_2d: list[list[float]], filter_2d: list[list[float]]) -> float:
    """2차원 배열 기반 MAC: 동일 위치 곱셈 후 누적."""
    n = len(input_2d)  # 2차원 행렬의 크기(가로/세로 길이)를 측정
    acc = 0.0  # 계산된 곱셈 결과들을 차곡차곡 더해 나갈 누적 변수 초기화
    for i in range(n):  # 세로 방향(행)을 차례대로 순회
        for j in range(n):  # 가로 방향(열)을 차례대로 순회
            acc += input_2d[i][j] * filter_2d[i][j]  # 입력 행렬과 필터 행렬의 같은 위치에 있는 값끼리 곱해서 누적
    return acc  # 최종적으로 계산된 총합(MAC 연산 결과)을 반환

def mac_1d(input_1d: list[float], filter_1d: list[float]) -> float:
    """1차원 배열 기반 MAC (최적화 버전)"""
    acc = 0.0  # 곱셈 결과를 차곡차곡 더해 누적할 변수 초기화
    for i in range(len(input_1d)):  # 1차원 리스트의 전체 길이만큼 처음부터 끝까지 순회
        acc += input_1d[i] * filter_1d[i]  # 두 1차원 리스트의 같은 인덱스에 있는 값끼리 곱해서 누적
    return acc  # 최종 연산 결과 총합 반환