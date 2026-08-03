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
from pipeline import validate_schema
from generator import generate_cross, generate_x
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

def run_console_mode() -> None:
    reporter.print_section(1, "입력 방식 선택")
    print("1. 3x3 필터/패턴 직접 입력")
    print("2. NxN 패턴 자동 생성기 사용 (보너스 과제)")
    choice = input("선택: ").strip()

    if choice == '1':
        reporter.print_section(1, "필터 입력 (3x3)")
        filter_a = _get_valid_matrix("필터 A (3줄 입력, 공백 구분)")
        print()
        filter_b = _get_valid_matrix("필터 B (3줄 입력, 공백 구분)")
        reporter.print_section(2, "패턴 입력")
        pattern = _get_valid_matrix("패턴 (3줄 입력, 공백 구분)")
    
    elif choice == '2':
        n = int(input("\n원하는 패턴의 크기 N을 입력하세요 (예: 3, 5, 13 등 홀수): "))
        if n % 2 == 0 or n < 3:
            print("중심점이 있는 패턴을 위해 3 이상의 홀수만 가능합니다.")
            return
        
        reporter.print_section(1, f"{n}x{n} 패턴 자동 생성 완료")
        filter_a = generate_cross(n)  # A를 Cross 필터로
        filter_b = generate_x(n)      # B를 X 필터로
        
        pat_type = input("테스트할 패턴 종류를 선택하세요 (1: 십자가, 2: X): ").strip()
        pattern = generate_cross(n) if pat_type == '1' else generate_x(n)
    
    else:
        print("잘못된 입력입니다.")
        return

    # [3] MAC 연산 → 성능 측정 → 판정 → 출력
    score_a = mac_2d(pattern, filter_a)
    score_b = mac_2d(pattern, filter_b)
    avg_sec = measure(mac_2d, pattern, filter_a)
    
    verdict = classify(score_a, score_b, 'A (Cross)', 'B (X)')
    if verdict == 'UNDECIDED':
        verdict = None
        
    reporter.print_mac_result(score_a, score_b, avg_sec, verdict, EPSILON)


# =========================================================
# 모드 2: data.json 분석
# =========================================================
def run_batch_mode(path: str = 'data.json') -> None:
    # JSON 파일 입출력 크래시 방지
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"\n[시스템 오류] '{path}' 파일을 찾을 수 없습니다.")
        print("data.json 파일이 올바른 위치에 있는지 확인해주세요.\n")
        return
    except json.JSONDecodeError as e:
        print(f"\n[데이터 오류] JSON 파일 형식이 잘못되었습니다. (파싱 실패: {e})\n")
        return

    # [1] 필터 로드
    reporter.print_section(1, "필터 로드")
    filters = data['filters']
    for name in filters:
        reporter.print_filter_loaded(name)

    # [2] 패턴 분석 (라벨 정규화 적용)
    reporter.print_section(2, "패턴 분석 (라벨 정규화 적용)")
    results = []
    
    for case_id, case in _iter_pattern_cases(data['patterns']):
        # 개별 케이스 격리 (하나가 에러나도 전체 루프는 계속 돌아감)
        try:
            # 1. 스키마 및 크기 무결성 사전 검증 (파이프라인 연결)
            validate_schema(case)
            
            pattern = case.get('input', case.get('pattern'))
            expected = normalize_label(case.get('expected'))

            if expected is None:
                _record_skip(results, case_id, expected, 'expected 라벨 누락 또는 미지원')
                continue

            size_key = _resolve_size_key(case_id, case, pattern, filters)

            if size_key not in filters:
                _record_skip(results, case_id, expected, f'{size_key} 필터 없음')
                continue

            # 2. MAC 연산 (에러 발생 가능 구간)
            filt_cross = filters[size_key]['cross']
            filt_x = filters[size_key]['x']
            s_cross = mac_2d(pattern, filt_cross)
            s_x = mac_2d(pattern, filt_x)

            # 3. 판정
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
            reporter.print_case_result(case_id, s_cross, s_x, verdict, expected, passed, note)
            
        except Exception as e:
            # 크기 불일치(IndexError), 필드 누락(ValueError) 등 모든 예외를 잡아서 격리!
            _record_skip(results, case_id, case.get('expected', '-'), f'불량 데이터 격리 (원인: {e})')
            continue

    # [3] 성능 분석 (3×3 포함 전 크기)
    perf_rows = profile_sizes(PERF_SIZES)
    reporter.print_perf_table(perf_rows)

    # [4] 결과 요약
    reporter.print_summary(results)