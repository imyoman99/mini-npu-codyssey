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

def main() -> None:
    memory_state = {}  # 메모리 상태를 저장하는 딕셔너리

    while True:
        reporter.print_header()
        try:
            mode = input("선택: ").strip()
        except EOFError:
            print("\n[종료] 입력이 종료되어 프로그램을 종료합니다.")
            break

        if mode == '1':
            run_console_mode(memory_state)
        elif mode == '2':
            run_batch_mode()
        elif mode == '0':
            print("\n[종료] 프로그램을 종료합니다. 이용해 주셔서 감사합니다.")
            break  
        else:
            print("\n 잘못된 선택입니다. 0, 1, 2 중에서 입력하세요.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Ctrl+C 강제 종료 시 안내 후 종료
        print("\n\n[종료] 사용자에 의해 프로그램이 안전하게 종료되었습니다.")
        sys.exit(0)