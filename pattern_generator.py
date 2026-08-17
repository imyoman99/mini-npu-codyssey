"""
pattern_generator.py — 패턴 자동 생성기 (보너스 과제)
"""

def generate_patterns(n: int):
    """
    크기 N을 입력받아 N*N 크기의 Cross 패턴과 X 패턴을 반환한다.
    반환값: (cross_pattern, x_pattern)
    """
    # 십자가 모양(Cross) 패턴 생성 (중앙 행 또는 중앙 열인 위치만 1.0, 나머지는 0.0)
    cross = [[1.0 if (i == n // 2 or j == n // 2) else 0.0 for j in range(n)] for i in range(n)]
    
    # X자 모양(X) 패턴 생성 (대각선 방향인 위치만 1.0, 나머지는 0.0)
    x_pat = [[1.0 if (i == j or i + j == n - 1) else 0.0 for j in range(n)] for i in range(n)]
    
    # 생성된 두 개의 2차원 패턴 튜플 형태로 반환
    return cross, x_pat