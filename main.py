"""
main.py — 유일한 진입점. 모드 선택 후 runner에 위임.
"""

import sys

# [버전 검증] Python 3.8 미만일 경우 실행 즉시 차단
if sys.version_info < (3, 8):
    print(f"[오류] 이 프로그램은 Python 3.8 이상 버전이 필요합니다. (현재: {sys.version.split()[0]})")
    sys.exit(1)

import reporter
from runner import run_console_mode, run_batch_mode


def main():
    reporter.print_header()
    mode = input("선택: ").strip()

    if mode == '1':
        run_console_mode()
    elif mode == '2':
        run_batch_mode()
    else:
        print("잘못된 선택입니다. 1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()