from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PyQt6.QtCore import Qt


_HTML = """
<div style="max-width: 760px; font-family: 'Malgun Gothic', 'Segoe UI', sans-serif; font-size: 10pt; color: #FFFFFF; line-height: 1.8;">

<h2 style="color:#FFFFFF; font-size:16pt; margin-bottom:4px;">AIIDEA란?</h2>
<p style="color:#FFFFFF; margin-top:0;">업무 생산성을 높이기 위한 <b>AI 기반 문서 작성 도우미</b>입니다.<br>
Gemini AI를 활용하여 회의록, 제안서, 보고서, 수익성 분석 등을 빠르게 작성할 수 있습니다.</p>

<h3 style="color:#FFFFFF; margin-top:28px;">주요 기능</h3>
<ul style="margin:0; padding-left:20px;">
  <li>📊 <b>보고서</b> — 업무 보고서 자동 초안 생성 및 Word/PDF 내보내기</li>
  <li>📄 <b>제안서</b> — 프로젝트 제안서 AI 작성 및 Word/PDF 내보내기</li>
  <li>💹 <b>수익성 분석</b> — 비용·수익 항목 입력 후 연도별 수익성 분석 및 AI 인풋값 제안</li>
  <li>📋 <b>회의록</b> — 회의 내용 입력 후 구조화된 회의록 자동 생성</li>
  <li>🗄 <b>DB 자료 저장</b> — 작성한 문서와 데이터를 로컬 데이터베이스에 저장 및 조회</li>
  <li>💬 <b>오류 및 개선방안</b> — 사용 중 발견한 오류나 개선 요청을 기록하여 전달</li>
</ul>

<hr style="border:none; border-top:1px solid #3A3A3A; margin:28px 0;">

<h3 style="color:#FFFFFF; margin-top:0;">📥 다운로드 방법</h3>
<ol style="margin:0; padding-left:20px;">
  <li>OneDrive → <b>내 파일 → Attachment</b> 폴더에 인스톨러 파일이 있습니다.</li>
  <li>브라우저에서 보안 경고로 다운로드를 거부할 수 있습니다.<br>
      → 다운로드 수가 적은 프로그램이라 그런 것이니 문제 없습니다!</li>
  <li>인스톨러를 실행하면 자동으로 설치됩니다.</li>
</ol>

<hr style="border:none; border-top:1px solid #3A3A3A; margin:28px 0;">

<h3 style="color:#FFFFFF; margin-top:0;">💡 사용 팁</h3>
<ul style="margin:0; padding-left:20px;">
  <li>AI가 <b>거짓 또는 없는 내용을 지어낼 수 있으므로</b>, 생성된 모든 정보는 꼭 직접 확인해주세요.</li>
  <li>입력값을 자세하게 작성할수록 더 좋은 결과물이 나옵니다.</li>
  <li>오류나 불편사항은 <b>오류 및 개선방안</b> 메뉴에서 보내주시면 수정 후 업데이트하겠습니다.</li>
</ul>

</div>
"""


class ManualWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("contentArea")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 헤더
        header = QWidget()
        header.setFixedHeight(64)
        header.setStyleSheet("background-color: #171717; border-bottom: 1px solid #3A3A3A;")
        from PyQt6.QtWidgets import QHBoxLayout
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 0, 24, 0)
        title = QLabel("📖  AIIDEA 사용설명서")
        title.setObjectName("pageTitle")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addWidget(header)

        # 스크롤 콘텐츠
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: #171717;")

        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #171717;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 32, 40, 40)
        content_layout.setSpacing(0)

        label = QLabel()
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setText(_HTML)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        label.setStyleSheet("background: transparent; color: #ECECEC;")
        content_layout.addWidget(label)
        content_layout.addStretch()

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
