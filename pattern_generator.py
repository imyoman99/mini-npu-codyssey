"""
pattern_generator.py — 패턴 자동 생성기 (보너스 과제)
"""

def generate_patterns(n: int):
    """
    크기 N을 입력받아 N*N 크기의 Cross 패턴과 X 패턴을 반환한다.
    반환값: (cross_pattern, x_pattern)
    """
    cross = [[1.0 if (i == n // 2 or j == n // 2) else 0.0 for j in range(n)] for i in range(n)]
    x_pat = [[1.0 if (i == j or i + j == n - 1) else 0.0 for j in range(n)] for i in range(n)]
    return cross, x_pat