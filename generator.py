"""
generator.py — N×N Cross / X 패턴 자동 생성기
벤치마크용 대형 패턴과, 판정용 필터를 모두 이 모듈이 공급한다.
"""


def _validate_size(n):
    if n < 3:
        raise ValueError(f"패턴 크기가 3 미만: {n}")
    if n % 2 == 0:
        raise ValueError(f"중심이 명확하도록 홀수 크기만 허용: {n}")


def generate_cross(n):
    """가운데 행/열이 1인 십자(+) 패턴 생성."""
    _validate_size(n)
    center = n // 2
    return [
        [1 if (i == center or j == center) else 0 for j in range(n)]
        for i in range(n)
    ]


def generate_x(n):
    """두 대각선이 1인 X 패턴 생성."""
    _validate_size(n)
    return [
        [1 if (i == j or i + j == n - 1) else 0 for j in range(n)]
        for i in range(n)
    ]