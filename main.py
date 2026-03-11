import sys
import os
from pathlib import Path


def main():
    # .env 파일 로드 (PyInstaller 빌드 시 .exe 옆, 개발 환경 시 프로젝트 루트)
    try:
        from dotenv import load_dotenv
        if getattr(sys, 'frozen', False):
            env_path = Path(sys.executable).parent / ".env"
        else:
            env_path = Path(__file__).parent / ".env"
        load_dotenv(env_path)
    except ImportError:
        pass

    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont, QIcon

    app = QApplication(sys.argv)
    app.setApplicationName("AIIDEA")
    app.setOrganizationName("AIIDEA")

    # 아이콘 설정 (타이틀바, 작업표시줄)
    if getattr(sys, 'frozen', False):
        icon_path = Path(sys.executable).parent / "_internal" / "icon.ico"
    else:
        icon_path = Path(__file__).parent / "assets" / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # 앱 기본 폰트 (point size는 반드시 1 이상이어야 Qt 경고 방지)
    font = QFont()
    font.setFamily("Malgun Gothic")
    font.setPointSize(10)
    app.setFont(font)

    # 전체 스타일시트 적용
    from app.ui.styles import MAIN_STYLESHEET
    app.setStyleSheet(MAIN_STYLESHEET)

    # 사용 로그 DB 초기화
    from app.logger import init_db
    init_db()

    from app.ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    # 이름 또는 API 키 미설정 시 초기 설정 다이얼로그 표시
    missing_name = not os.environ.get("USER_NAME", "").strip()
    missing_key  = not os.environ.get("GEMINI_API_KEY", "").strip()
    if missing_name or missing_key:
        window._open_settings(first_run=True)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
