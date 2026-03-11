<div align="center">

# ✦ AIIDEA

**Gemini AI 기반 업무 문서 자동화 Windows 데스크탑 앱**

회의록 · 제안서 · 보고서 · 수익성 분석 초안을 AI가 자동으로 작성합니다.

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/UI-PyQt6-41CD52?style=flat-square)
![Gemini](https://img.shields.io/badge/AI-Gemini-4285F4?style=flat-square&logo=google&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white)

</div>

---

## 1. 기존 AI 도구의 한계

> ChatGPT, Gemini, Perplexity 같은 범용 챗봇을 **실무 문서 작성**에 쓰면 이런 문제가 생깁니다.

| ❌ 한계                       | 문제 상황                                              |
| ----------------------------- | ------------------------------------------------------ |
| 토큰 제한으로 인한 분량 부족  | 긴 문서 요청 시 내용이 중간에 잘리고 뒷부분이 빈약해짐 |
| 툴 파편화로 인한 비효율       | 여러 AI 툴을 넘나들며 결과물을 수동으로 취합해야 함    |
| 할루시네이션 검증 불가        | 오류 내용인지 아닌지 구분 없이 생성되어 전체 검수 필요 |
| 창작과 사실의 경계 모호       | 수치·출처를 지어내는 경향이 있어 신뢰도 문제 발생      |
| Word/Excel 변환의 어려움      | 생성 후 서식을 수동으로 맞춰야 해 추가 작업 발생       |
| 프롬프트 비표준화로 품질 편차 | 매번 다른 프롬프트로 결과물 품질이 들쭉날쭉            |
| 입력값의 한계                 | 자유형 텍스트 하나로 전달하다 보니 정보 누락이 잦음    |
| 섹션 간 유기성 부족           | 대화 나눠 생성 시 앞뒤 내용이 어긋나고 논리가 끊김     |

---

## 2. AIIDEA가 다른 이유

> AIIDEA는 **문서 유형별 전용 워크플로우**로 위 한계를 구조적으로 해결합니다.

| ✅ 한계                | AIIDEA의 접근 방식                                           |
| ---------------------- | ------------------------------------------------------------ |
| 토큰 제한·분량 부족    | 목차 생성 → 섹션별 분할 생성으로 끊김 없이 완성              |
| 툴 파편화              | 하나의 앱에서 모든 문서 유형 처리                            |
| 할루시네이션·사실 혼용 | 사용자가 입력한 핵심 데이터를 기반으로 AI가 살을 붙이는 구조 |
| Word/Excel 변환        | 생성 즉시 `.docx` / `.xlsx` / `.pdf` 원클릭 내보내기         |
| 프롬프트 비표준화      | 문서 유형별 최적화 프롬프트 내장으로 항상 일정한 품질        |
| 입력값 한계            | 항목별 입력 폼으로 누락 없이 구조화된 데이터 전달            |
| 섹션 간 유기성 부족    | 목차 확정 후 전체 구조를 AI에 전달해 일관된 맥락 유지        |

---

## 3. 주요 기능

| 모듈                    | 설명                                                                      |
| ----------------------- | ------------------------------------------------------------------------- |
| 📋 **회의록**           | 회의 정보 입력 → AI 자동 생성 → Word / PDF 내보내기                       |
| 📄 **제안서**           | 단계별 입력 → AI 작성 → Word / PDF 내보내기                               |
| 📊 **보고서**           | 주제 입력 → AI 목차 생성 → 섹션별 본문 작성 → Word / PDF 내보내기         |
| 💹 **수익성 분석**      | 비용 / 매출 입력 → 자동 계산 + 차트 → Excel / PDF 내보내기                |
| 🗄️ **DB 자료 저장**     | txt / docx / xlsx 파일 등록 → AI가 내용을 참고해 문서 작성                |
| 💬 **오류 및 개선사항** | 앱 내에서 오류 제보 및 개선 아이디어 이메일 자동 전송                     |
| 📈 **실행이력조회**     | AI 생성 시 사용자명 · 문서 종류 · 제목 · 시간을 Google Sheets에 자동 기록 |

---

## 4. 설치

### 요구사항

- Python **3.13+**
- Windows

### 패키지 설치

```bash
pip install -r requirements.txt
```

### 환경 변수 설정

`.env.example`을 복사해서 `.env`로 이름을 바꾸고 값을 채웁니다.

```bash
cp .env.example .env
```

```env
GEMINI_API_KEY=발급받은_Gemini_API_키

SMTP_EMAIL=발신용_Gmail_주소
SMTP_PASSWORD=Gmail_앱_비밀번호
RECEIVER_EMAIL=피드백_수신_이메일

GSHEET_WEBHOOK_URL=Google_Apps_Script_웹훅_URL   # 선택

USER_NAME=사용자_이름
```

| 항목                 | 발급 방법                                                  |
| -------------------- | ---------------------------------------------------------- |
| `GEMINI_API_KEY`     | [Google AI Studio](https://aistudio.google.com/) 에서 발급 |
| `SMTP_PASSWORD`      | Gmail → 보안 → 2단계 인증 → **앱 비밀번호** 생성           |
| `GSHEET_WEBHOOK_URL` | Google Sheets + Apps Script 웹훅 URL (선택사항)            |

---

## 5. 실행

```bash
py main.py
```

---

## 6. 프로젝트 구조

```
Aiidea/
├── main.py
├── requirements.txt
├── .env.example                # 환경 변수 템플릿 (Git 포함)
├── .env                        # 실제 키 / 비밀번호 (Git 제외)
└── app/
    ├── ai_client.py            # Gemini API 클라이언트
    ├── file_utils.py           # 파일 저장 경로 유틸
    ├── logger.py               # 사용 로그 (Google Sheets)
    ├── ui/
    │   ├── main_window.py      # 메인 윈도우
    │   ├── sidebar.py          # 좌측 네비게이션
    │   └── styles.py           # 다크 테마 QSS
    └── modules/
        ├── meeting_minutes/    # 회의록
        ├── proposal/           # 제안서
        ├── report/             # 보고서
        ├── profitability/      # 수익성 분석
        ├── db/                 # DB 자료 저장
        ├── feedback/           # 오류 & 개선사항 전송
        └── manual/             # 사용 설명서
```

---

## 7. 기술 스택

| 분류          | 라이브러리                         |
| ------------- | ---------------------------------- |
| UI            | PyQt6                              |
| AI            | Google Gemini API (`google-genai`) |
| 문서 내보내기 | python-docx · reportlab · openpyxl |
| 차트          | matplotlib                         |
| 환경 변수     | python-dotenv                      |

---

## 8. 오류 및 개선사항

앱 사용 중 오류를 발견하거나 개선 아이디어가 있다면 아래 방법으로 전달해주세요.

**앱 내 전송**

1. 좌측 사이드바 → **오류 및 개선방안** 클릭
2. 제목과 내용 입력 후 **전송** 클릭
3. 검토 후 다음 업데이트에 반영됩니다

**GitHub Issues**

- 직접 이슈를 등록해도 됩니다.

---
