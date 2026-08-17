"""
main.py — 유일한 진입점. 모드 선택 후 runner에 위임.
"""

import sys

# [버전 검증] Python 3.8 미만일 경우 실행 즉시 차단
if sys.version_info < (3, 8):
    print(f"[오류] 이 프로그램은 Python 3.8 이상 버전이 필요합니다. (현재: {sys.version.split()[0]})")
    sys.exit(1)  # 3.8 미만 버전이면 에러 코드 1을 반환하며 프로그램 강제 종료

import reporter
from runner import run_console_mode, run_batch_mode

def main() -> None:
    memory_state = {}  # 메모리 상태(패턴 크기, 생성된 패턴 등)를 저장할 빈 딕셔너리 초기화

    while True:
        reporter.print_header()  # 프로그램 메인 메뉴 화면 출력
        try:
            mode = input("선택: ").strip()  # 사용자로부터 실행할 모드 번호 입력받고 공백 제거
        except EOFError:
            # 입력 스트림이 끊긴 경우(Ctrl+D 등) 예외 처리 후 안전하게 종료
            print("\n[종료] 입력이 종료되어 프로그램을 종료합니다.")
            break

        if mode == '1':
            run_console_mode(memory_state)  # 1번 모드: 대화형 콘솔 모드 실행 (메모리 상태 전달)
        elif mode == '2':
            run_batch_mode()  # 2번 모드: 일괄 처리(배치) 모드 실행
        elif mode == '0':
            print("\n[종료] 프로그램을 종료합니다. 이용해 주셔서 감사합니다.")
            break  # 반복문 탈출 후 프로그램 종료
        else:
            print("\n 잘못된 선택입니다. 0, 1, 2 중에서 입력하세요.")  # 메뉴 번호 외의 값이 입력된 경우 경고

if __name__ == "__main__":
    try:
        main()  # 스크립트가 직접 실행된 경우 main 함수 호출
    except KeyboardInterrupt:
        # 사용자가 키보드로 강제 종료(Ctrl+C)한 경우 예외를 잡아 깔끔하게 메시지 출력 후 종료
        print("\n\n[종료] 사용자에 의해 프로그램이 안전하게 종료되었습니다.")
        sys.exit(0)