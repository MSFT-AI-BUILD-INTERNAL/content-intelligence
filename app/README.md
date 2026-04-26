# Azure AI Foundry — Content Intelligence Sample

Azure **Content Understanding** 및 **Document Intelligence** 서비스를 **Azure Managed Identity**로 연동하는 Python 샘플 앱입니다. API Key는 사용하지 않습니다.

## 프로젝트 구조

```
app/
├── core/                              # 공통 인프라
│   ├── auth.py                        #   인증 (DefaultAzureCredential)
│   ├── config.py                      #   환경 변수 / 경로 설정
│   ├── llm.py                         #   LLM 호출 (구조화 출력)
│   ├── models.py                      #   Pydantic 모델
│   ├── prompts.py                     #   프롬프트 로더
│   └── prompts.yaml                   #   시스템 / 태스크 프롬프트
├── services/                          # Azure 서비스 래퍼
│   ├── content_understanding.py       #   Content Understanding 클라이언트
│   └── document_intelligence.py       #   Document Intelligence 클라이언트
├── samples/                           # CLI 데모 스크립트
│   ├── content_understanding.py       #   CU 샘플 실행
│   └── document_intelligence.py       #   DI 샘플 실행
├── web/                               # 웹 애플리케이션
│   ├── app.py                         #   FastAPI 라우트
│   └── templates/index.html           #   웹 UI
├── sample_files/                      # 테스트 문서 (PDF, 이미지)
├── main.py                            # CLI 진입점
├── pyproject.toml
└── .env.example
```

## 사전 요구 사항

1. **Azure Managed Identity** 설정
   - Azure VM, App Service, Container App 등에서 System-assigned 또는 User-assigned Managed Identity 활성화
   - 해당 Identity에 **Cognitive Services User** 역할(RBAC)을 AI Foundry 리소스에 할당

2. **로컬 개발 시**: `az login` 또는 VS Code Azure 확장을 통해 인증

3. **Python 3.10+**

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
| `CONTENT_UNDERSTANDING_ENDPOINT` | Content Understanding 리소스 엔드포인트 |
| `AZURE_OPENAI_ENDPOINT` | Azure AI Foundry 리소스 엔드포인트 (v1 API) |
| `LLM_DEPLOYMENT` | LLM 배포 이름 (구조화 출력용) |
| `DOCUMENT_INTELLIGENCE_ENDPOINT` | Document Intelligence 엔드포인트 |

## 실행

```bash
# 전체 실행
uv run python main.py

# Content Understanding만
uv run python main.py content-understanding

# Document Intelligence만
uv run python main.py document-intelligence

# 웹 앱 실행
uv run uvicorn web.app:app --host 0.0.0.0 --port 8000 --reload
```

## 주요 기능

### Content Understanding (`services/content_understanding.py`)
- `prebuilt-layout` 분석기로 문서 마크다운 추출
- LLM으로 `DocumentSummary` / 영수증 필드 JSON 구조화 출력

### Document Intelligence (`services/document_intelligence.py`)
- `prebuilt-layout` — 레이아웃 분석
- `prebuilt-read` — OCR 텍스트 추출
- `prebuilt-receipt` — 영수증 필드 추출
- LLM으로 구조화된 JSON 정제

### 구조화 출력 (`core/llm.py`, `core/models.py`)
- Pydantic 모델 기반 (`DocumentSummary`)
- Azure AI Foundry LLM을 통해 원본 텍스트를 구조화된 JSON으로 정제
- `json_schema` response format을 사용한 Structured Output 보장

## 인증 방식

이 앱은 `DefaultAzureCredential`을 사용하여 다음 순서로 인증을 시도합니다:

1. 환경 변수 (Service Principal)
2. Managed Identity (Azure 호스팅 환경)
3. Azure CLI (`az login`)
4. VS Code Azure 확장
5. Azure PowerShell

> ⚠️ **API Key 기반 인증은 의도적으로 지원하지 않습니다.**
