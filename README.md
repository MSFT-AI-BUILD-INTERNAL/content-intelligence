# Content Intelligence

Azure **Document Intelligence** + **LLM** 기반 문서 분석 웹 애플리케이션입니다.  
Azure Managed Identity 인증을 사용하며, API Key는 사용하지 않습니다.

## 주요 기능

- **Document Intelligence** — `prebuilt-layout` 모델로 문서에서 마크다운 추출 (PDF, 이미지 등)
- **LLM 구조화 출력** — 추출된 텍스트를 Azure OpenAI로 JSON 구조화 (문서 요약, 영수증 분석)
- **실시간 메트릭** — DI 응답 시간, LLM 응답 시간, 토큰 사용량, 페이지 수 표시
- **웹 UI** — FastAPI + 단일 HTML 페이지로 파일 선택 → 분석 → 결과 조회

## 아키텍처

```
Azure Blob Storage  →  Document Intelligence  →  LLM (Azure OpenAI)  →  Web UI
     (파일 원본)         (마크다운 추출)           (구조화 출력)         (결과 표시)
```

## 프로젝트 구조

```
├── init.sh                            # VM 초기 설정 스크립트
├── app/
│   ├── core/                          # 공통 인프라
│   │   ├── auth.py                    #   인증 (DefaultAzureCredential)
│   │   ├── config.py                  #   환경 변수 / 경로 설정
│   │   ├── llm.py                     #   LLM 호출 (구조화 출력 + 토큰 사용량)
│   │   ├── models.py                  #   Pydantic 모델
│   │   ├── prompts.py                 #   프롬프트 로더
│   │   └── prompts.yaml               #   시스템 / 태스크 프롬프트
│   ├── services/                      # Azure 서비스 래퍼
│   │   ├── blob_storage.py            #   Blob Storage 클라이언트
│   │   ├── content_understanding.py   #   Content Understanding (legacy)
│   │   └── document_intelligence.py   #   Document Intelligence (primary)
│   ├── samples/                       # CLI 데모 스크립트
│   │   ├── content_understanding.py   #   DI 기반 샘플 실행
│   │   └── document_intelligence.py   #   DI 레이아웃/영수증 샘플
│   ├── web/                           # 웹 애플리케이션
│   │   ├── app.py                     #   FastAPI 라우트
│   │   └── templates/index.html       #   웹 UI
│   ├── sample_files/                  # 테스트 문서 (PDF, 이미지)
│   ├── main.py                        # CLI 진입점
│   ├── pyproject.toml                 # 프로젝트 설정 및 의존성
│   └── .env.example                   # 환경 변수 템플릿
```

## 사전 요구 사항

1. **Azure VM** (Ubuntu 20.04+ 권장)에 System-assigned Managed Identity 활성화
2. 해당 Identity에 다음 RBAC 역할 할당:
   - **Cognitive Services User** → Document Intelligence + AI Foundry 리소스
   - **Storage Blob Data Reader** → Blob Storage 계정
3. **Python 3.10+**

## VM 설치 및 실행

```bash
# 1. 리포지토리 클론
git clone https://github.com/MSFT-AI-BUILD-INTERNAL/content-intelligence.git
cd content-intelligence

# 2. 초기 설정 (Azure CLI, uv, 의존성 설치)
chmod +x init.sh
./init.sh

# 3. 환경 변수 확인/수정
vi app/.env

# 4. 웹 앱 실행
cd app
uv run python main.py web
# → http://<VM-IP>:8000 에서 접속
```

## 환경 변수

| 변수 | 설명 |
|------|------|
| `DOCUMENT_INTELLIGENCE_ENDPOINT` | Document Intelligence 엔드포인트 |
| `AZURE_OPENAI_ENDPOINT` | Azure AI Foundry 리소스 엔드포인트 (v1 API) |
| `LLM_DEPLOYMENT` | LLM 배포 이름 (기본: `gpt-5.2-chat`) |
| `BLOB_ACCOUNT_URL` | Azure Blob Storage 계정 URL |
| `BLOB_CONTAINER` | Blob 컨테이너 이름 (기본: `data`) |
| `BLOB_PREFIX` | Blob 접두사 (기본: `invoices/`) |

## CLI 실행

```bash
cd app

# 웹 앱 (기본)
uv run python main.py web

# Document Intelligence 샘플
uv run python main.py content-understanding

# DI 레이아웃/영수증 샘플
uv run python main.py document-intelligence

# 전체 샘플 실행
uv run python main.py all
```

## 인증 방식

`DefaultAzureCredential`을 사용하여 다음 순서로 인증을 시도합니다:

1. 환경 변수 (Service Principal)
2. Managed Identity (Azure VM 환경)
3. Azure CLI (`az login`)
4. VS Code Azure 확장

> ⚠️ API Key 기반 인증은 지원하지 않습니다.

## API 응답 예시

```json
{
  "filename": "receipt.pdf",
  "document_intelligence": { "markdown": "..." },
  "llm_analysis": {
    "document_summary": { "title": "...", "summary": "..." },
    "receipt_summary": { "total": 45000, "merchant_name": "..." }
  },
  "metrics": {
    "di_page_count": 2,
    "di_response_time_ms": 1230,
    "llm_response_time_ms": 2450,
    "llm_token_usage": {
      "prompt_tokens": 512,
      "completion_tokens": 248,
      "total_tokens": 760
    }
  }
}
```