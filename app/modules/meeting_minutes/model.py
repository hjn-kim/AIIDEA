import dataclasses
import re


@dataclasses.dataclass
class MeetingMinutes:
    title: str = ""
    host: str = ""
    purpose: str = ""
    meeting_datetime: str = ""
    location: str = ""
    attendees: str = ""
    agenda: str = ""
    details: str = ""
    decisions: str = ""
    next_steps: str = ""

    def is_empty(self) -> bool:
        return not any([self.title, self.agenda, self.details])


def make_meeting_prompt(m: "MeetingMinutes") -> str:
    # 주최측·장소는 값이 있을 때만 포함
    optional_lines = []
    if m.host.strip():
        optional_lines.append(f"- 주최측: {m.host}")
    if m.location.strip():
        optional_lines.append(f"- 장소: {m.location}")
    optional_block = "\n".join(optional_lines)

    # 빈 항목은 AI가 추론하도록 지시
    def _field(label: str, value: str) -> str:
        if value.strip():
            return f"- {label}: {value}"
        return f"- {label}: (입력값 없음 — 회의 제목·목적·참석자 정보를 바탕으로 AI가 합리적으로 작성)"

    agenda_line   = _field("안건 / 주요 논의 사항", m.agenda)
    details_line  = _field("세부 논의 내용", m.details)
    decisions_line = _field("결정사항", m.decisions)

    return f"""당신은 전문 회의록 작성 비서입니다.
아래 회의 정보를 바탕으로 완성도 높은 한국어 회의록을 작성하세요.

[회의 정보]
- 회의 제목: {m.title}
- 회의 목적: {m.purpose}
- 일시: {m.meeting_datetime}
- 참석자: {m.attendees}
{optional_block}
{agenda_line}
{details_line}
{decisions_line}

[작성 지침]
- 각 섹션은 반드시 "## 섹션제목" 형식으로 시작하세요.
- 아래 4개 섹션을 순서대로 작성하세요:
  ## 1. 주요 안건 및 논의 내용
  ## 2. 세부 논의 내용
  ## 3. 결정사항
  ## 4. 향후 계획 및 후속조치
- "(입력값 없음)" 으로 표시된 항목은 다른 회의 정보를 참고하여 현실적으로 추론해 작성하세요.
- 각 항목은 "- " 으로 시작하는 불릿 포인트로 작성하세요.
- 입력된 내용을 구조화·보완하여 전문적인 문체로 작성하세요.
- 불필요한 인사말, 머리말, 꼬리말 없이 섹션 내용만 출력하세요.
"""


def parse_ai_sections(text: str) -> list[tuple[str, str]]:
    """## 제목 기준으로 섹션 파싱 → [(제목, 내용), ...]"""
    parts = re.split(r"^##\s+", text, flags=re.MULTILINE)
    result = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lines = part.split("\n", 1)
        heading = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        result.append((heading, body))
    return result
