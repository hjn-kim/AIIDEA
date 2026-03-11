import dataclasses
import re

STYLES = ["줄글형", "Bullet 항목형", "줄글 + Bullet 항목형"]


@dataclasses.dataclass
class Report:
    title: str = ""
    purpose: str = ""
    author: str = ""
    date: str = ""
    volume: str = "일반 (A4 10p)"
    style: str = "줄글형"
    requirements: str = ""

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def make_toc_prompt(r: "Report") -> str:
    volume_info = r.volume or "미정"
    return f"""너는 컨설팅 보고서 작성 전문가다.
아래 입력을 바탕으로 보고서 목차(TOC)를 한국어로 작성하라.

[절대 준수 — 마크다운·서식 기호 완전 금지]
**, *, ##, ###, #, ~~, `, > 등 마크다운 기호와 특수 서식 문자를 단 하나라도 사용하면 출력 전체가 폐기된다.
굵기·기울임·강조 등 어떠한 서식도 적용하지 말 것. 오직 순수 텍스트만 허용한다.

[입력]
- 보고서 제목: {r.title}
- 보고서 목적: {r.purpose or "미정"}
- 작성자: {r.author or "미정"}
- 총 분량: {volume_info}
- 조건/요구사항: {r.requirements or "없음"}

[출력 요구사항]
- 출력은 번호가 매겨진 목차 항목만 포함해야 한다.
- 제목, 설명, 안내문, 라벨을 절대 출력하지 말 것.
- "목차", "개정 목차", "개정목차"라는 문자열을 어떤 형태로도 출력하지 말 것.
- 번호 체계는 1, 1.1, 1.2 형태로 작성.
- 최소 5개 장(Chapter) 이상.
- 장(1,2,3...)과 소절(1.1, 1.2...)로 구성.
- 총 분량({volume_info}페이지)을 모든 소절의 중요도에 비례하여 배분하라.
- 각 소절(1.1, 1.2 형태) 제목 끝에 반드시 배분된 분량을 (Xp) 형식으로 표기하라. 예: 1.1 시장 현황 분석 (8p)
- 장(1, 2, 3...) 항목에는 분량을 표기하지 말 것.
- 모든 소절의 분량 합계가 총 분량과 일치하도록 배분하라.
- 불필요한 설명문 없이 목차만 출력.""".strip()



def _extract_page_hint(chapter_title: str) -> str:
    m = re.search(r"\((\d+)p\)", chapter_title)
    if m:
        return f"이 소절의 분량은 약 {m.group(1)}페이지이므로 그에 맞는 깊이와 길이로 작성하라."
    return ""


def make_section_prompt(chapter_title: str, r: "Report", summary_context: str = "") -> str:
    volume_hint = _extract_page_hint(chapter_title)
    return f"""너는 대형 컨설팅펌 수준의 전문 보고서를 작성하는 최고 수준의 분석가이다.
아래 입력 정보를 바탕으로 해당 소제목에 대해 고품질 보고서를 작성하라.
{volume_hint}

[절대 준수 — 마크다운·서식 기호 완전 금지]
**, *, ##, ###, #, ~~, `, > 등 마크다운 기호와 특수 서식 문자를 단 하나라도 사용하면 출력 전체가 폐기된다.
굵기·기울임·강조 등 어떠한 서식도 적용하지 말 것. 오직 순수 텍스트만 허용한다.

[입력]
- 해당 소제목: {chapter_title}
- 보고서 제목: {r.title}
- 보고서 목적: {r.purpose or "미정"}
- 보고서 요구사항: {r.requirements or "없음"}
- 서술방식: {r.style}
- 이전 내용 요약: {summary_context or "없음"}

[출력 요구사항]
1. REPORT
- 서술방식이 '줄글형'이면 본문을 문단 형태의 줄글로 작성하여라
- 서술방식이 'Bullet 항목형'인 경우,  줄글형 서술을 지양하고 '-' 기호로 시작하는 불릿 형식으로 작성하여 종결은 명사, '함', '하였음' 중 사용할 것.
- 줄글+Bullet 항목형은 필요에 따라 줄글과 불릿 항목형을 섞어 서술하라.
- “해당 소제목”에 정확히 대응하는 심층적이고 장문의 본문을 작성하라.
- 단순 설명을 지양하고, 원인·구조·배경·영향·시사점의 관점에서 심층적이고 전문적인 분석을 수행하라.
- 해당 주제에 대해 객관적 사실에 기반한 정확한 분석을 제공하라.
- 관련 데이터(통계, 조사 결과, 시장 동향)와 사례(기존 연구, 산업 사례, 국가·지역 비교)를 적극 활용하여 논리를 강화하라.
- 이전 내용 요약을 참고하여 논리적 흐름이 자연스럽게 이어지도록 작성하라.
- 내용은 보고서 목적에 직접적으로 부합하도록 구성하라.
- 장 제목과 소제목은 “1. 서론”, “1.1 정의”와 같은 형태로만 작성하라.
- 모든 본문은 빈 줄 없이 작성하라.
- 문단은 필요한 경우에만 구분할 수 있으며, 문단이 바뀔 때에는 단일 줄바꿈만 허용한다.
- 문단 내부의 일반 서술 문장 사이에는 줄바꿈을 사용하지 마라.
- 연속된 줄바꿈(빈 줄)은 절대 사용하지 마라.
- 소제목 바로 아래에도 빈 줄을 두지 마라.
- 검증되지 않은 사실, 확인되지 않은 통계는 절대 작성하지 마라.

2. SUMMARY
- 해당 소제목의 핵심 내용을 정확히 2문장으로 요약하라.

3. SOURCES
- 본문 작성에 실제 활용된 외부 출처를 MLA 형식으로 기재하라.
- 실제로 존재하고 실제로 사용한 공신력 자료만 기재하라.
- 확실한 출처를 특정할 수 없는 경우 기재하지 마라.
- 출처가 없으면 출처없음을 표현하지 말고 빈칸으로 출력하여라. 

[출력 형식]
반드시 아래 3개 블록만으로 출력하라.

[REPORT]
(해당 소제목 보고서 본문)
[/REPORT]

[SUMMARY]
(핵심 요약 2문장)
[/SUMMARY]

[SOURCES]
(MLA 형식 출처 목록)
[/SOURCES]""".strip()


def extract_chapters(toc: str) -> list:
    """소절(1.1, 1.2, 1.1.1 ...)만 추출 — 장(1, 2, 3)은 제목만이므로 제외"""
    chapters = []
    pattern = re.compile(r"^\s*(\d+\.\d+(?:\.\d+)*)\s*[\.\)]?\s+.+")
    for line in (toc or "").splitlines():
        s = line.strip().replace("*", "")
        if pattern.match(s):
            chapters.append(s.rstrip(":").strip())
    return chapters


def parse_response_blocks(text: str, chapter_title: str = "") -> tuple:
    t = (text or "").strip()
    if not t:
        return f"{chapter_title} (내용 없음)", "", ""

    def between_pair(txt, a, b):
        if a not in txt or b not in txt:
            return ""
        return txt.split(a, 1)[1].split(b, 1)[0].strip()

    report = between_pair(t, "[REPORT]", "[/REPORT]")
    summary = between_pair(t, "[SUMMARY]", "[/SUMMARY]")
    sources = between_pair(t, "[SOURCES]", "[/SOURCES]")
    if report:
        return report, summary, sources
    return t, "", ""
