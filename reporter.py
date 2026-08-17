"""
reporter.py — 모든 화면 출력 형식 전담
"""

import unicodedata

def get_display_width(text):
    """한글(2칸)과 영문/숫자(1칸)의 콘솔 출력 너비를 정확히 계산합니다."""
    width = 0
    for char in text:
        # 'F'(Fullwidth), 'W'(Wide) 속성을 가진 문자는 한글 등 동아시아 문자 (2칸 차지)
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            width += 2
        else:
            width += 1
    return width

def print_section(num, title):
    content = f"# [{num}] {title}"  # 섹션 번호와 제목을 조합하여 마크다운 헤더 형태의 문자열 생성
    display_width = get_display_width(content)  # 조합된 문자열이 터미널 화면에서 차지하는 실제 너비(글자 폭)를 계산
    
    # 계산된 글자 너비에 맞춰 상단/하단 '-' 선의 길이를 동적으로 조절!
    line = "#" + "-" * (display_width - 1)
    
    print()
    print(line)
    print(content)
    print(line)


def print_header():
    print("\n=== Mini NPU Simulator ===")
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    print("0. 종료")


# --- 모드 1 ---
def print_mode1_submenu():
    print("\n[모드 1: 사용자 입력 및 패턴 생성]")
    print("1. 3x3 필터 및 패턴 직접 입력")
    print("2. 패턴 생성기")
    print("0. 메인 메뉴로 돌아가기")


def print_mac_result(score_a, score_b, t_a_2d, t_a_1d, t_b_2d, t_b_1d, verdict, epsilon):
    print_section(3, "MAC 연산 결과 (직접 입력한 패턴)")
    
    print(f"[필터 A 매칭] 점수: {score_a} | 2D: {t_a_2d*1e3:.3f} ms | 1D: {t_a_1d*1e3:.3f} ms")
    print(f"[필터 B 매칭] 점수: {score_b} | 2D: {t_b_2d*1e3:.3f} ms | 1D: {t_b_1d*1e3:.3f} ms")
    
    if verdict is None or verdict == 'UNDECIDED':
        print(f"판정: 판정 불가 (|A-B| < {epsilon})")
    else:
        print(f"판정: {verdict}")


def print_generated_pattern_result(pat_type, score_a, score_b, t_a_2d, t_a_1d, t_b_2d, t_b_1d, verdict):
    # 보너스 출력문구도 깔끔하게 통일감을 주었습니다.
    print()
    title = f"* [자동 생성 '{pat_type}' 패턴 성능 분석]"
    width = get_display_width(title)
    print(title)
    print("-" * width)
    
    print(f"[필터 A 매칭] 점수: {score_a} | 2D: {t_a_2d*1e3:.3f} ms | 1D: {t_a_1d*1e3:.3f} ms")
    print(f"[필터 B 매칭] 점수: {score_b} | 2D: {t_b_2d*1e3:.3f} ms | 1D: {t_b_1d*1e3:.3f} ms")
    print(f"판정: {verdict}")


# --- 모드 2 ---
def print_filter_loaded(name):
    print(f"✓ {name}  필터 로드 완료 (Cross, X)")


def print_case_result(case_id, s_cross, s_x, verdict, expected, passed, reason=""):
    print(f"--- {case_id} ---")
    print(f"Cross 점수: {s_cross}")
    print(f"X 점수: {s_x}")
    tail = f" ({reason})" if reason else ""
    print(f"판정: {verdict} | expected: {expected} | {'PASS' if passed else 'FAIL'}{tail}")


def print_perf_table(rows):
    """rows: [(n, 2d_sec, 1d_sec), ...]"""
    print_section(3, "성능 분석 (2D vs 1D 최적화 비교)")
    print(f"{'크기':<8}{'2D 시간(ms)':>13}{'1D 시간(ms)':>13}{'연산 횟수':>10}")
    print("-" * 46)
    for n, sec_2d, sec_1d in rows:
        print(f"{f'{n}×{n}':<8}{sec_2d * 1e3:>13.3f}{sec_1d * 1e3:>13.3f}{n * n:>10}")


def print_summary(results):
    """results: [(case_id, passed, reason), ...]"""
    print_section(4, "결과 요약")
    fails = [(cid, r) for cid, ok, r in results if not ok]
    print(f"총 테스트: {len(results)}개")
    print(f"통과: {len(results) - len(fails)}개")
    print(f"실패: {len(fails)}개")
    if fails:
        print("\n실패 케이스:")
        for cid, reason in fails:
            print(f"- {cid}: {reason}")