"""
reporter.py — 모든 화면 출력 형식 전담
"""

LINE = "#" + "-" * 39


def print_header():
    print("=== Mini NPU Simulator ===\n")
    print("[모드 선택]\n")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")


def print_section(num, title):
    print()
    print(LINE)
    print(f"# [{num}] {title}")
    print(LINE)


# --- 모드 1 ---

def print_mac_result(score_a, score_b, avg_sec, verdict, epsilon):
    if verdict is None or verdict == 'UNDECIDED':  # 판정 불가
        print_section(3, "MAC 결과 (판정 불가)")
        print(f"A 점수: {score_a}")
        print(f"B 점수: {score_b}")
        print(f"판정: 판정 불가 (|A-B| < {epsilon})")
    else:
        print_section(3, "MAC 결과")
        print(f"A 점수: {score_a}")
        print(f"B 점수: {score_b}")
        print(f"연산 시간(평균/10회): {avg_sec * 1e3:.3f} ms")
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
    """rows: [(n, 평균초), ...]"""
    print_section(3, "성능 분석 (평균/10회)")
    print(f"{'크기':<10}{'평균 시간(ms)':>14}{'연산 횟수':>12}")
    print("-" * 37)
    for n, sec in rows:
        print(f"{f'{n}×{n}':<10}{sec * 1e3:>14.3f}{n * n:>12}")


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