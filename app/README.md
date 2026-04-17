# Azure AI Foundry — Content Intelligence Sample

Azure **Content Understanding** 및 **Document Intelligence** 서비스를 **Azure Managed Identity**로 연동하는 Python 샘플 앱입니다. API Key는 사용하지 않습니다.

## 아키텍처

```
┌─────────────────────────────────────────────────┐
│                   main.py                       │
│         (CLI entry — 서비스 선택/전체 실행)        │
├────────────────────┬────────────────────────────┤
│  Content           │  Document                  │
│  Understanding     │  Intelligence              │
│  Sample            │  Sample                    │
├────────────────────┴────────────────────────────┤
│              auth.py                            │
│   DefaultAzureCredential (Managed Identity)     │
├─────────────────────────────────────────────────┤
│              config.py (.env)                   │
│   Endpoints configuration                       │
└─────────────────────────────────────────────────┘
```

## 사전 요구 사항

1. **Azure Managed Identity** 설정
   - Azure VM, App Service, Container App 등에서 System-assigned 또는 User-assigned Managed Identity 활성화
   - 해당 Identity에 **Cognitive Services User** 역할(RBAC)을 AI Foundry 리소스에 할당

2. **로컬 개발 시**: `az login` 또는 VS Code Azure 확장을 통해 인증

3. **Python 3.9+**

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

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `FOUNDRY_ENDPOINT` | AI Foundry 프로젝트 엔드포인트 | `https://jinsungpark-westus-resource.services.ai.azure.com/api/projects/jinsungpark-westus` |
| `LLM_DEPLOYMENT` | LLM 배포 이름 (구조화 출력용) | `gpt-4o` |
| `DOCUMENT_INTELLIGENCE_ENDPOINT` | Document Intelligence 엔드포인트 | `https://jinsungpark-westus-resource.cognitiveservices.azure.com/` |

## 실행

```bash
# 전체 실행
uv run python main.py

# Content Understanding만
uv run python main.py content-understanding

# Document Intelligence만
uv run python main.py document-intelligence
```

## 샘플 파일

`sample_files/trip-receipt.pdf`를 분석 대상으로 사용합니다.

## 주요 기능

### Content Understanding (`content_understanding_sample.py`)
- **문서 분석** — `prebuilt-documentSearch` → LLM으로 `DocumentSummary` JSON 출력
- **영수증 필드 추출** — `prebuilt-receipt` → LLM으로 `ReceiptSummary` JSON 출력

### Document Intelligence (`document_intelligence_sample.py`)
- **레이아웃 + OCR 분석** — `prebuilt-layout` + `prebuilt-read` → LLM으로 `DocumentSummary` JSON 출력
- **영수증 분석** — `prebuilt-receipt` → LLM으로 `ReceiptSummary` JSON 출력

### 구조화 출력 (`models.py`, `llm.py`)
- Pydantic 모델 기반 (`ReceiptSummary`, `DocumentSummary`)
- Foundry 프로젝트의 LLM (gpt-4o)을 통해 원본 텍스트를 구조화된 JSON으로 정제
- `JsonSchemaFormat`을 사용한 Structured Output 보장

## 인증 방식

이 앱은 `DefaultAzureCredential`을 사용하여 다음 순서로 인증을 시도합니다:

1. 환경 변수 (Service Principal)
2. Managed Identity (Azure 호스팅 환경)
3. Azure CLI (`az login`)
4. VS Code Azure 확장
5. Azure PowerShell

> ⚠️ **API Key 기반 인증은 의도적으로 지원하지 않습니다.**
