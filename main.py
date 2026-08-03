"""
main.py — 유일한 진입점. 모드 선택 후 runner에 위임.
"""

import sys

# [버전 검증] Python 3.8 미만일 경우 실행 즉시 차단
if sys.version_info < (3, 8):
    print(f"[오류] 이 프로그램은 Python 3.8 이상 버전이 필요합니다. (현재: {sys.version.split()[0]})")
    sys.exit(1)

import reporter
from runner import run_console_mode, run_batch_mode, run_generator_mode

def main() -> None:
    # 🔥 무한 루프 시작: 사용자가 0을 누를 때까지 프로그램이 끝나지 않습니다.
    while True:
        reporter.print_header()
        mode = input("선택: ").strip()

        if mode == '1':
            run_console_mode()
        elif mode == '2':
            run_batch_mode()
        elif mode == '3':
            run_generator_mode()
        elif mode == '0':
            print("\n[종료] 프로그램을 종료합니다. 이용해 주셔서 감사합니다.")
            break  # 루프 탈출 -> 프로그램 정상 종료
        else:
            print("\n 잘못된 선택입니다. 0, 1, 2, 3 중에서 입력하세요.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Ctrl+C 강제 종료 시 지저분한 Traceback을 숨기고 우아하게 종료
        print("\n\n[종료] 사용자에 의해 프로그램이 안전하게 종료되었습니다.")
        sys.exit(0)