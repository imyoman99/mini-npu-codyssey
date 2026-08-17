"""
pipeline.py — 분석 파이프라인 코어
패턴 하나를 받아 MAC → 판정까지 수행하는 순수 로직.
입출력(콘솔/JSON)을 전혀 모른다 → 어디서든 재사용 가능.
"""

from mac_engine import mac_2d
from classifier import classify


def analyze(pattern_2d):
    """패턴 → (cross점수, x점수, 판정). 파이프라인의 공통 코어."""
    n = len(pattern_2d)  # 패턴의 크기(n x n) 확인
    
    # 십자가 모양(Cross) 필터 자동 생성 (중앙 행 또는 중앙 열인 위치만 1.0, 나머지는 0.0)
    cross_filter = [[1.0 if (i == n // 2 or j == n // 2) else 0.0 for j in range(n)] for i in range(n)]
    
    # X자 모양(X) 필터 자동 생성 (대각선 방향인 위치만 1.0, 나머지는 0.0)
    x_filter = [[1.0 if (i == j or i + j == n - 1) else 0.0 for j in range(n)] for i in range(n)]
    
    # 생성된 Cross 필터와 X 필터를 사용해 각각 MAC 연산 점수 계산
    score_cross = mac_2d(pattern_2d, cross_filter)
    score_x = mac_2d(pattern_2d, x_filter)
    
    # 두 점수를 비교하여 최종 판정 결과를 포함한 튜플(Cross점수, X점수, 판정결과) 반환
    return score_cross, score_x, classify(score_cross, score_x)


def validate_schema(case):
    """JSON 케이스 스키마 사전 검증. 문제 시 ValueError."""
    # 1. 'input'이나 'pattern' 둘 중 하나라도 필드가 아예 없으면 에러 발생
    if 'input' not in case and 'pattern' not in case:
        raise ValueError("'input' 또는 'pattern' 필드 누락")

    # 2. 둘 중 존재하는 값을 가져와서 패턴 데이터로 지정
    pattern = case.get('input', case.get('pattern'))
    n = len(pattern)
    
    # 3. 패턴의 크기(행 개수)가 최소 3 미만이면 에러 발생
    if n < 3:
        raise ValueError(f"패턴 크기가 3 미만: {n}")
        
    # 4. 각 행(row)의 열 개수가 전체 크기(n)와 맞지 않으면 에러 발생 (정사각형 형태 검증)
    for row in pattern:
        if len(row) != n:
            raise ValueError(f"행 길이 불일치: {len(row)} != {n}")