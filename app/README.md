# Azure AI Foundry — Content Intelligence App

Azure **Document Intelligence** 기반 문서 분석 + **LLM** 구조화 출력 Python 앱입니다.  
Azure Managed Identity 인증을 사용합니다 (API Key 미사용).

## 프로젝트 구조

```
app/
├── core/                              # 공통 인프라
│   ├── auth.py                        #   인증 (DefaultAzureCredential)
│   ├── config.py                      #   환경 변수 / 경로 설정
│   ├── llm.py                         #   LLM 호출 (구조화 출력 + 토큰 사용량)
│   ├── models.py                      #   Pydantic 모델
│   ├── prompts.py                     #   프롬프트 로더
│   └── prompts.yaml                   #   시스템 / 태스크 프롬프트
├── services/                          # Azure 서비스 래퍼
│   ├── blob_storage.py                #   Blob Storage 클라이언트
│   ├── content_understanding.py       #   Content Understanding (legacy)
│   └── document_intelligence.py       #   Document Intelligence (primary)
├── samples/                           # CLI 데모 스크립트
│   ├── content_understanding.py       #   DI 기반 샘플
│   └── document_intelligence.py       #   DI 레이아웃/영수증 샘플
├── web/                               # 웹 애플리케이션
│   ├── app.py                         #   FastAPI 라우트
│   └── templates/index.html           #   웹 UI
├── sample_files/                      # 테스트 문서 (PDF, 이미지)
├── main.py                            # CLI 진입점
├── pyproject.toml
└── .env.example
```

## 설치

[uv](https://docs.astral.sh/uv/)를 사용하여 패키지를 관리합니다.

```bash
cd app
uv sync          # 가상환경 생성 + 의존성 설치
```

> `uv`가 없는 경우: `curl -LsSf https://astral.sh/uv/install.sh | sh`

## 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 열어 엔드포인트를 확인/수정하세요
```

| 변수 | 설명 |
|------|------|
| `DOCUMENT_INTELLIGENCE_ENDPOINT` | Document Intelligence 엔드포인트 |
| `AZURE_OPENAI_ENDPOINT` | Azure AI Foundry 리소스 엔드포인트 (v1 API) |
| `LLM_DEPLOYMENT` | LLM 배포 이름 (구조화 출력용) |
| `BLOB_ACCOUNT_URL` | Azure Blob Storage 계정 URL |
| `BLOB_CONTAINER` | Blob 컨테이너 이름 |
| `BLOB_PREFIX` | Blob 접두사 (파일 경로) |

## 실행

```bash
# 웹 앱 실행 (기본)
uv run python main.py web

# Document Intelligence 샘플
uv run python main.py content-understanding

# DI 레이아웃/영수증 샘플
uv run python main.py document-intelligence

# 전체 샘플 실행
uv run python main.py all
```

## 주요 기능

### Document Intelligence (`services/document_intelligence.py`)
- `prebuilt-layout` 분석기로 문서 마크다운 추출 (Markdown 출력 형식)
- 페이지 수 반환
- 바이트 입력 및 파일 경로 입력 모두 지원

### LLM 구조화 출력 (`core/llm.py`)
- Pydantic 모델 기반 (`DocumentSummary`)
- Azure AI Foundry LLM을 통해 원본 텍스트를 구조화된 JSON으로 정제
- `json_schema` response format을 사용한 Structured Output 보장
- **토큰 사용량** (prompt/completion/total) 반환

### 웹 UI 메트릭
- 📄 Document Intelligence 처리 페이지 수
- ⚡ Document Intelligence 응답 시간
- 🤖 LLM 처리 응답 시간
- 🪙 토큰 사용량 (입력/출력/합계)

## 인증 방식

이 앱은 `DefaultAzureCredential`을 사용하여 다음 순서로 인증을 시도합니다:

1. 환경 변수 (Service Principal)
2. Managed Identity (Azure 호스팅 환경)
3. Azure CLI (`az login`)
4. VS Code Azure 확장
5. Azure PowerShell

> ⚠️ **API Key 기반 인증은 의도적으로 지원하지 않습니다.**
