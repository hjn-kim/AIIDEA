import os
from PyQt6.QtCore import QThread, pyqtSignal

SYSTEM_PROMPTS = {
    "meeting_summary": (
        "당신은 전문 비즈니스 회의록 작성 전문가입니다.\n"
        "주어진 회의 내용을 분석하여 다음 형식으로 한국어 회의록 요약을 작성하세요:\n"
        "1. 핵심 논의 사항\n"
        "2. 결정 사항\n"
        "3. 후속 조치 및 담당자\n"
        "명확하고 간결한 비즈니스 문체를 사용하세요."
    ),
    "meeting_draft": (
        "당신은 전문 비즈니스 회의록 작성 전문가입니다.\n"
        "제공된 안건과 참석자 정보를 바탕으로 전문적인 회의록 초안을 작성하세요.\n"
        "실제 회의에서 논의될 법한 내용을 구조적으로 작성하세요."
    ),
    "proposal_section": (
        "당신은 전문 비즈니스 제안서 작성 전문가입니다.\n"
        "제공된 맥락을 바탕으로 제안서의 해당 섹션을 전문적이고 설득력 있게 작성하세요.\n"
        "한국어 비즈니스 문체를 사용하며, 구체적이고 실행 가능한 내용을 포함하세요."
    ),
    "proposal_review": (
        "당신은 전문 비즈니스 제안서 검토 전문가입니다.\n"
        "제공된 제안서 전체를 검토하고 다음을 분석하세요:\n"
        "1. 논리적 일관성\n"
        "2. 설득력 개선 포인트\n"
        "3. 누락된 중요 내용\n"
        "4. 언어 및 문체 개선사항\n"
        "구체적인 개선 제안을 포함하세요."
    ),
    "report_section": (
        "당신은 전문 경영 보고서 작성 전문가입니다.\n"
        "주어진 데이터와 내용을 바탕으로 명확하고 전문적인 보고서 섹션을 작성하세요.\n"
        "데이터 기반의 인사이트와 명확한 결론을 포함하세요."
    ),
    "report_summary": (
        "당신은 전문 경영 보고서 작성 전문가입니다.\n"
        "제공된 보고서 전체 내용을 바탕으로 경영진을 위한 간결한 Executive Summary를 작성하세요.\n"
        "핵심 내용, 주요 성과, 중요 이슈, 권고사항을 포함하세요."
    ),
    "report_proofread": (
        "당신은 한국어 비즈니스 문서 교정 전문가입니다.\n"
        "제공된 텍스트를 검토하여 다음을 수정하세요:\n"
        "1. 맞춤법 및 문법 오류\n"
        "2. 비즈니스 문체로 개선\n"
        "3. 명확성 향상\n"
        "수정된 전체 텍스트를 출력하세요."
    ),
    "profitability_analysis": (
        "당신은 시니어 재무 분석가입니다.\n"
        "제공된 수익성 분석 데이터를 검토하고 다음을 포함하는 전문 분석 리포트를 한국어로 작성하세요:\n"
        "1. 핵심 재무 지표 요약\n"
        "2. 손익분기점 분석 해석\n"
        "3. ROI 및 수익성 평가\n"
        "4. 시나리오별 위험 평가\n"
        "5. 전략적 권고사항\n"
        "전문적이고 명확한 비즈니스 언어를 사용하세요."
    ),
    "profitability_input_setup": (
        "당신은 시니어 비즈니스 및 재무 분석가입니다.\n"
        "사업 정보를 분석하여 수익성 분석에 필요한 비용·수익 항목을 파이프(|) 구분 형식으로 제공하세요.\n"
        "다른 텍스트, 헤더, 마크다운 없이 오직 데이터 행만 출력하세요."
    ),
}


class AIWorker(QThread):
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, prompt: str, system_key: str = "", model: str = "", parent=None):
        super().__init__(parent)
        self.prompt = prompt
        self.system_key = system_key
        self.model = model

    def run(self):
        try:
            client = GeminiClient.get_instance()
            system = SYSTEM_PROMPTS.get(self.system_key, "")
            result = client.generate(self.prompt, system, model=self.model or None)
            self.result_ready.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))


class GeminiClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        cls._instance = None

    def __init__(self):
        from google import genai
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
        self.client = genai.Client(api_key=api_key)
        self.model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

    def generate(self, prompt: str, system_prompt: str = "", model: str = None) -> str:
        if system_prompt:
            full = f"{system_prompt}\n\n---\n\n{prompt}"
        else:
            full = prompt
        response = self.client.models.generate_content(
            model=model or self.model,
            contents=full,
        )
        return response.text
