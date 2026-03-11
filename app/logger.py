"""
사용 로그 — Google Sheets (Apps Script 웹훅)
.env 의 GSHEET_WEBHOOK_URL 에 웹훅 URL 설정 시 전송, 없으면 무시.
"""
import os
import json
import threading
from datetime import datetime


def init_db() -> None:
    """하위 호환용 no-op (main.py 에서 호출)."""
    pass


def log_usage(doc_type: str, doc_title: str) -> None:
    """AI 생성 버튼 클릭 시 호출. 별도 스레드로 비동기 전송."""
    webhook_url = os.environ.get("GSHEET_WEBHOOK_URL", "").strip()
    if not webhook_url:
        return

    user_name = os.environ.get("USER_NAME", "미설정").strip() or "미설정"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payload = json.dumps({
        "name": user_name,
        "doc_type": doc_type,
        "doc_title": doc_title,
        "timestamp": now,
    }).encode("utf-8")

    def _send():
        try:
            import http.client
            import urllib.parse

            parsed = urllib.parse.urlparse(webhook_url)
            conn = http.client.HTTPSConnection(parsed.netloc, timeout=10)
            # 리다이렉트 없이 POST만 전송 — 스크립트는 서버에서 즉시 실행됨
            conn.request(
                "POST",
                parsed.path + ("?" + parsed.query if parsed.query else ""),
                body=payload,
                headers={"Content-Type": "application/json"},
            )
            conn.getresponse()  # 응답 소비 (302 무시)
            conn.close()
        except Exception:
            pass  # 로그 실패가 앱 동작을 막아선 안 됨

    threading.Thread(target=_send, daemon=True).start()
