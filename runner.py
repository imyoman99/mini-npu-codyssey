"""
runner.py — 모드별 실행 흐름 (입력 → 연산 → 판정 → 성능 → 요약)
- 모드 1: 필터 A/B 입력 → 패턴 입력 → MAC/판정 → 성능(3×3)
- 모드 2: 필터 로드 → 패턴 분석/PASS-FAIL → 성능(3~25) → 결과 요약
"""

import json

from mac_engine import mac_2d, mac_1d
from normalizer import normalize_label
from classifier import classify, EPSILON
from benchmark import measure, profile_sizes
from pipeline import validate_schema
import reporter
from pattern_generator import generate_patterns

PERF_SIZES = [3, 5, 13, 25]  # 모드 2 성능 분석 대상 크기


def _read_matrix(rows=3, cols=3):
    matrix = []  # 행렬 데이터를 담을 빈 리스트 생성
    for i in range(rows):  # 지정된 행(row) 개수만큼 반복
        values = [float(x) for x in input().split()]  # 입력을 받아 실수(float)로 변환한 리스트 생성
        if len(values) != cols:  # 입력된 값의 개수가 필요한 열(col) 개수와 다르면
            raise ValueError(f"{i + 1}행을 입력했습니다 {cols}개 값이 필요합니다 (입력: {len(values)}개)")  # 에러 발생
        matrix.append(values)  # 정상적인 행 데이터를 행렬에 추가
    return matrix  # 완성된 2차원 행렬 반환


def _iter_pattern_cases(patterns):
    if isinstance(patterns, dict):
        return patterns.items()  # 딕셔너리인 경우 키와 값 쌍을 그대로 반환
    if isinstance(patterns, list):
        return ((case.get('id', str(index)), case) for index, case in enumerate(patterns))  # 리스트인 경우 각 요소에 ID를 부여해 딕셔너리 형태로 변환하여 반환
    raise TypeError('patterns는 딕셔너리(dict) 또는 리스트(list)여야 합니다')  # 그 외의 타입이 들어오면 에러 발생


def _resolve_size_key(case_id, case, pattern, filters):
    size_key = case.get('size')  # 데이터에서 'size' 값을 안전하게 가져옴
    if isinstance(size_key, str) and size_key in filters:
        return size_key  # 1순위: 직접 지정된 사이즈가 유효하면 즉시 반환

    if isinstance(case_id, str) and '_' in case_id:
        inferred = case_id.rsplit('_', 1)[0]
        if inferred in filters:
            return inferred  # 2순위: ID의 뒷부분을 떼어내서 추론한 값이 유효하면 반환

    inferred = f"size_{len(pattern)}"
    if inferred in filters:
        return inferred  # 3순위: 패턴의 길이를 이용해 만든 이름이 유효하면 반환

    return size_key or inferred  # 최후의 수단: 둘 다 없으면 기본값(size_key 또는 추론값) 반환


def _record_skip(results, case_id, expected, reason):
    results.append((case_id, False, reason))    # 결과 목록에 실패/스킵 상태(False)와 사유를 기록
    reporter.print_case_result(case_id, '-', '-', 'SKIP',   # 양식에 맞춰 스킵 내역을 콘솔에 출력   
                               expected if expected else '-',
                               False, reason)


# =========================================================
# 모드 1: 사용자 입력 및 패턴 생성 (3x3)
# =========================================================
def _get_valid_matrix(prompt_msg):
    while True:  # 올바른 행렬을 입력할 때까지 무한 반복
        print(prompt_msg)  # 사용자에게 안내 메시지(프롬프트) 출력
        try:
            return _read_matrix()  # 행렬 읽기 시도 (앞서 본 _read_matrix 함수 호출)
        except ValueError as e:  # 입력 개수 안 맞음의 에러가 발생하면
            print(f"\n[입력 형식 오류] {e}")  # 발생한 에러 메시지 출력
            print("다시 입력해주세요.\n")  # 재입력 안내 후 반복문 처음으로 돌아가 재시도


def run_console_mode(memory_state: dict) -> None:
    while True:  # 콘솔 모드 메뉴를 무한 반복하며 사용자 입력을 대기
        reporter.print_mode1_submenu()  # 하위 메뉴 화면(선택지) 출력
        choice = input("선택: ").strip()  # 사용자로부터 메뉴 번호를 입력받고 공백 제거

        if choice == '1':  # 1번: 필터 및 패턴 입력 후 성능 분석 실행
            reporter.print_section(1, "필터 입력 (3x3)")
            filter_a = _get_valid_matrix("필터 A (3줄 입력, 공백 구분)")  # 유효한 필터 A 행렬 입력받기
            print()                                                  # 가독성을 위한 여백
            filter_b = _get_valid_matrix("필터 B (3줄 입력, 공백 구분)")  # 유효한 필터 B 행렬 입력받기

            reporter.print_section(2, "패턴 입력")
            pattern = _get_valid_matrix("패턴 (3줄 입력, 공백 구분)")  # 유효한 패턴 행렬 입력받기

            # 2차원 행렬을 1차원 리스트로 평탄화(Flatten)
            filter_a_1d = [val for row in filter_a for val in row]
            filter_b_1d = [val for row in filter_b for val in row]
            pattern_1d = [val for row in pattern for val in row]

            # 2차원 연산(MAC) 수행하여 점수 계산
            score_a = mac_2d(pattern, filter_a)
            score_b = mac_2d(pattern, filter_b)

            # 필터 A, B 각각 2D 및 1D 연산 시간 측정
            t_a_2d = measure(mac_2d, pattern, filter_a)
            t_a_1d = measure(mac_1d, pattern_1d, filter_a_1d)
            t_b_2d = measure(mac_2d, pattern, filter_b)
            t_b_1d = measure(mac_1d, pattern_1d, filter_b_1d)

            # 두 점수를 비교하여 판정 결과 도출 (결과가 UNDECIDED면 None으로 처리)
            verdict = classify(score_a, score_b, 'Filter A', 'Filter B')
            if verdict == 'UNDECIDED':
                verdict = None

            # 일반 입력 패턴 분석 결과 출력
            reporter.print_mac_result(score_a, score_b, t_a_2d, t_a_1d, t_b_2d, t_b_1d, verdict, EPSILON)

            # 메모리에 저장된 패턴 크기가 3x3일 때 보너스 분석 실행
            if memory_state.get('size') == 3:
                reporter.print_section(4, "보너스: 자동 생성된 패턴과 입력 필터의 성능 분석")
                
                # 1) 메모리에 있는 Cross 패턴 성능 측정
                cross_pat = memory_state['cross']
                cross_pat_1d = [val for row in cross_pat for val in row]
                
                c_score_a = mac_2d(cross_pat, filter_a)
                c_score_b = mac_2d(cross_pat, filter_b)
                
                c_t_a_2d = measure(mac_2d, cross_pat, filter_a)
                c_t_a_1d = measure(mac_1d, cross_pat_1d, filter_a_1d)
                c_t_b_2d = measure(mac_2d, cross_pat, filter_b)
                c_t_b_1d = measure(mac_1d, cross_pat_1d, filter_b_1d)
                
                c_verdict = classify(c_score_a, c_score_b, 'A (Cross)', 'B (X)')
                if c_verdict == 'UNDECIDED': c_verdict = '판정 불가'
                
                reporter.print_generated_pattern_result("Cross(십자가)", c_score_a, c_score_b, c_t_a_2d, c_t_a_1d, c_t_b_2d, c_t_b_1d, c_verdict)

                # 2) 메모리에 있는 X 패턴 성능 측정
                x_pat = memory_state['x']
                x_pat_1d = [val for row in x_pat for val in row]
                
                x_score_a = mac_2d(x_pat, filter_a)
                x_score_b = mac_2d(x_pat, filter_b)
                
                x_t_a_2d = measure(mac_2d, x_pat, filter_a)
                x_t_a_1d = measure(mac_1d, x_pat_1d, filter_a_1d)
                x_t_b_2d = measure(mac_2d, x_pat, filter_b)
                x_t_b_1d = measure(mac_1d, x_pat_1d, filter_b_1d)

                x_verdict = classify(x_score_a, x_score_b, 'A (Cross)', 'B (X)')
                if x_verdict == 'UNDECIDED': x_verdict = '판정 불가'
                
                reporter.print_generated_pattern_result("X(엑스)", x_score_a, x_score_b, x_t_a_2d, x_t_a_1d, x_t_b_2d, x_t_b_1d, x_verdict)
                
            elif memory_state.get('size') is not None:
                # 메모리에 패턴이 있지만 3x3이 아닐 경우 안내 문구 출력 후 보너스 분석 생략
                print(f"\n* 참고: 메모리에 {memory_state['size']}x{memory_state['size']} 크기의 패턴이 "
                      "생성되어 있으나, 현재 3x3 필터 입력 모드이므로 연산 및 출력을 생략합니다.")

        elif choice == '2':  # 2번: 사용자 지정 크기(N)로 패턴 자동 생성
            try:
                n = int(input("\n생성할 패턴의 크기 N을 입력하세요 (홀수 권장, 예: 3): "))
                if n < 3:
                    print("[안내] 크기는 3 이상이어야 합니다.")
                    continue
                
                cross_pat, x_pat = generate_patterns(n)  # N 크기의 Cross 및 X 패턴 생성
                memory_state['size'] = n                 # 메모리에 패턴 크기 저장
                memory_state['cross'] = cross_pat        # 메모리에 Cross 패턴 저장
                memory_state['x'] = x_pat                # 메모리에 X 패턴 저장
                
                print(f"\n[성공] {n}x{n} 크기의 Cross 및 X 패턴이 메모리에 안전하게 생성되었습니다.")
            except ValueError:
                print("\n[오류] 올바른 숫자를 입력하세요.")  # 숫자가 아닌 값이 입력된 경우 예외 처리

        elif choice == '0':  # 0번: 콘솔 모드 종료 후 메인 메뉴로 복귀
            print("\n메인 메뉴로 돌아갑니다.")
            break
        else:
            print("\n잘못된 선택입니다. 0, 1, 2 중에서 입력하세요.")  # 메뉴 번호 외의 값이 입력된 경우 경고

# =========================================================
# 모드 2: data.json 분석
# =========================================================
def run_batch_mode(path: str = 'data.json') -> None:
    # 지정된 경로의 JSON 파일을 열어 데이터를 로드 (파일이 없거나 형식이 잘못된 경우 예외 처리)
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"\n[시스템 오류] '{path}' 파일을 찾을 수 없습니다.")
        return
    except json.JSONDecodeError as e:
        print(f"\n[데이터 오류] JSON 파일 형식이 잘못되었습니다. (파싱 실패: {e})\n")
        return

    reporter.print_section(1, "필터 로드")
    filters = data['filters']
    for name in filters:
        reporter.print_filter_loaded(name)  # 로드된 필터들의 이름을 화면에 출력

    reporter.print_section(2, "패턴 분석 (라벨 정규화 적용)")
    results = []  # 테스트 결과들을 모아둘 빈 리스트

    # 패턴 데이터를 하나씩 순회 (앞서 보았던 _iter_pattern_cases 함수 사용)
    for case_id, case in _iter_pattern_cases(data['patterns']):
        try:
            validate_schema(case)  # 데이터 구조(Schema)가 올바른지 검사
            pattern = case.get('input', case.get('pattern'))  # 입력 패턴 가져오기
            expected = normalize_label(case.get('expected'))  # 기대값(라벨) 가져와서 정규화

            # 기대값(expected)이 없으면 스킵 기록 후 다음 패턴으로 건너뜀
            if expected is None:
                _record_skip(results, case_id, expected, 'expected 라벨 누락 또는 미지원')
                continue

            # 적절한 사이즈 키를 판별 (앞서 보았던 _resolve_size_key 함수 사용)
            size_key = _resolve_size_key(case_id, case, pattern, filters)
            if size_key not in filters:
                _record_skip(results, case_id, expected, f'{size_key} 필터 없음')
                continue

            # 해당 사이즈의 Cross 및 X 필터를 가져와서 2차원 연산(MAC) 수행
            filt_cross = filters[size_key]['cross']
            filt_x = filters[size_key]['x']
            s_cross = mac_2d(pattern, filt_cross)
            s_x = mac_2d(pattern, filt_x)

            # 계산된 점수를 바탕으로 최종 판정(classify) 수행
            verdict = classify(s_cross, s_x)
            if verdict == 'UNDECIDED':
                passed = False
                reason = '동점(UNDECIDED) 처리 규칙에 따라 FAIL'
                note = '동점 규칙'
            else:
                passed = (verdict == expected)  # 판정 결과가 기대값과 일치하는지 확인
                reason = '' if passed else '판정 불일치'
                note = ''

            # 정상적으로 테스트가 끝난 결과를 리스트에 추가하고 화면에 출력
            results.append((case_id, passed, reason))
            reporter.print_case_result(case_id, s_cross, s_x, verdict, expected, passed, note)

        except Exception as e:
            # 처리 도중 알 수 없는 에러가 나면 프로그램이 죽지 않도록 잡아서 스킵 처리
            _record_skip(results, case_id, case.get('expected', '-'), f'불량 데이터 격리 (원인: {e})')
            continue

    # 모든 패턴 분석이 끝난 후, 성능 프로파일링 테이블과 전체 요약 통계 출력
    perf_rows = profile_sizes(PERF_SIZES)
    reporter.print_perf_table(perf_rows)
    reporter.print_summary(results)