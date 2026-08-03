"""
runner.py — 모드별 실행 흐름 (입력 → 연산 → 판정 → 성능 → 요약)
- 모드 1: 필터 A/B 입력 → 패턴 입력 → MAC/판정 → 성능(3×3)
- 모드 2: 필터 로드 → 패턴 분석/PASS-FAIL → 성능(3~25) → 결과 요약
"""

import json

from mac_engine import mac_2d
from normalizer import normalize_label
from classifier import classify, EPSILON
from benchmark import measure, profile_sizes
import reporter

PERF_SIZES = [3, 5, 13, 25]  # 모드 2 성능 분석 대상 크기


def _read_matrix(rows=3, cols=3):
    """콘솔에서 rows×cols 행렬을 읽는다. 열 개수가 맞지 않으면 ValueError."""
    matrix = []
    for i in range(rows):
        values = [float(x) for x in input().split()]
        if len(values) != cols:
            raise ValueError(f"{i + 1}행: {cols}개 값이 필요합니다 (입력: {len(values)}개)")
        matrix.append(values)
    return matrix


def _iter_pattern_cases(patterns):
    """dict/list 양쪽 스키마를 (case_id, case) 쌍으로 통일해서 순회한다."""
    if isinstance(patterns, dict):
        return patterns.items()
    if isinstance(patterns, list):
        return ((case.get('id', str(index)), case) for index, case in enumerate(patterns))
    raise TypeError('patterns must be a dict or list')


def _resolve_size_key(case_id, case, pattern, filters):
    """필터 키 결정 우선순위: 명시적 size → case_id 파싱 → 패턴 행 수 유도."""
    size_key = case.get('size')
    if isinstance(size_key, str) and size_key in filters:
        return size_key

    if isinstance(case_id, str) and '_' in case_id:
        inferred = case_id.rsplit('_', 1)[0]
        if inferred in filters:
            return inferred

    inferred = f"size_{len(pattern)}"
    if inferred in filters:
        return inferred

    return size_key or inferred


def _record_skip(results, case_id, expected, reason):
    """SKIP 케이스의 기록/출력을 한 곳에서 처리한다 (append → print 순서 통일)."""
    results.append((case_id, False, reason))
    reporter.print_case_result(case_id, '-', '-', 'SKIP',
                               expected if expected else '-',
                               False, reason)


# =========================================================
# 모드 1: 사용자 입력 (3x3)
# =========================================================
def _get_valid_matrix(prompt_msg):
    """올바른 행렬이 입력될 때까지 예외를 잡고 재입력을 유도하는 함수"""
    while True:
        print(prompt_msg)
        try:
            return _read_matrix()
        except ValueError as e:
            # 에러 발생 시 종료되지 않고 안내 문구 출력 후 다시 반복
            print(f"\n[입력 형식 오류] {e}")
            print("다시 입력해주세요.\n")

def run_console_mode():
    # [1] 필터 입력
    reporter.print_section(1, "필터 입력")
    filter_a = _get_valid_matrix("필터 A (3줄 입력, 공백 구분)")
    print()
    filter_b = _get_valid_matrix("필터 B (3줄 입력, 공백 구분)")

    # [2] 패턴 입력
    reporter.print_section(2, "패턴 입력")
    pattern = _get_valid_matrix("패턴 (3줄 입력, 공백 구분)")

    # [3] MAC 연산 → 성능 측정(3×3) → 판정 → 출력
    score_a = mac_2d(pattern, filter_a)
    score_b = mac_2d(pattern, filter_b)
    avg_sec = measure(mac_2d, pattern, filter_a)
    verdict = classify(score_a, score_b, 'A', 'B')
    if verdict == 'UNDECIDED':
        verdict = None  # reporter의 "판정 불가" 출력 규약
    reporter.print_mac_result(score_a, score_b, avg_sec, verdict, EPSILON)


# =========================================================
# 모드 2: data.json 분석
# =========================================================
def run_batch_mode(path='data.json'):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    # [1] 필터 로드
    reporter.print_section(1, "필터 로드")
    filters = data['filters']
    for name in filters:
        reporter.print_filter_loaded(name)

    # [2] 패턴 분석 (라벨 정규화 적용)
    reporter.print_section(2, "패턴 분석 (라벨 정규화 적용)")
    results = []  # (case_id, passed, reason) — [4] 요약에서 사용
    for case_id, case in _iter_pattern_cases(data['patterns']):
        pattern = case.get('input', case.get('pattern'))
        expected = normalize_label(case.get('expected'))

        if pattern is None:
            _record_skip(results, case_id, expected, '입력 패턴 누락')
            continue

        if expected is None:
            _record_skip(results, case_id, expected, 'expected 라벨 누락 또는 미지원')
            continue

        size_key = _resolve_size_key(case_id, case, pattern, filters)

        if size_key not in filters:
            _record_skip(results, case_id, expected, f'{size_key} 필터 없음')
            continue

        # MAC 연산: Cross / X 필터 각각
        filt_cross = filters[size_key]['cross']
        filt_x = filters[size_key]['x']
        s_cross = mac_2d(pattern, filt_cross)
        s_x = mac_2d(pattern, filt_x)

        # 판정: classify()는 동점 시 'UNDECIDED'를 반환한다.
        verdict = classify(s_cross, s_x)
        if verdict == 'UNDECIDED':
            passed = False
            reason = '동점(UNDECIDED) 처리 규칙에 따라 FAIL'
            note = '동점 규칙'
        else:
            passed = (verdict == expected)
            reason = '' if passed else '판정 불일치'
            note = ''

        results.append((case_id, passed, reason))
        reporter.print_case_result(case_id, s_cross, s_x,
                                   verdict, expected, passed, note)

    # [3] 성능 분석 (3×3 포함 전 크기)
    perf_rows = profile_sizes(PERF_SIZES)
    reporter.print_perf_table(perf_rows)

    # [4] 결과 요약
    reporter.print_summary(results)