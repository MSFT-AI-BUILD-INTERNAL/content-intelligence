"""
Web application for Document Intelligence + LLM analysis.

Files are loaded from Azure Blob Storage (not local filesystem).
Run: uvicorn web.app:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from core.llm import extract_raw, extract_structured
from core.models import DocumentSummary
from core.prompts import get_instruction
from services.blob_storage import download_file, list_files
from services.document_intelligence import analyze_bytes

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

app = FastAPI(title="Content Intelligence Web")


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main HTML page."""
    html_path = TEMPLATES_DIR / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.get("/api/files")
async def api_list_files():
    """Return list of files from Azure Blob Storage."""
    try:
        files = list_files()
    except Exception:
        logger.exception("Failed to list blobs")
        raise HTTPException(status_code=502, detail="Failed to list files from storage")
    return {"files": files}


@app.post("/api/analyze/{filename}")
async def analyze_file(filename: str):
    """Download a file from Blob Storage and run Document Intelligence + LLM analysis."""
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # Download from Blob Storage
    try:
        data, content_type = download_file(filename)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        logger.exception("Failed to download blob: %s", filename)
        raise HTTPException(status_code=502, detail="Failed to download file from storage")

    # --- Document Intelligence: extract markdown ---
    t0 = time.time()
    markdown, page_count = analyze_bytes(data, content_type)
    di_elapsed_ms = round((time.time() - t0) * 1000)

    # --- LLM Structured Output ---
    t1 = time.time()
    doc_summary, doc_usage = extract_structured(
        markdown,
        DocumentSummary,
        instruction=get_instruction("document_summary"),
    )

    receipt_summary, receipt_usage = extract_raw(
        markdown,
        instruction=get_instruction("receipt_extraction"),
    )
    llm_elapsed_ms = round((time.time() - t1) * 1000)

    # Aggregate token usage
    total_usage = {
        "prompt_tokens": doc_usage["prompt_tokens"] + receipt_usage["prompt_tokens"],
        "completion_tokens": doc_usage["completion_tokens"] + receipt_usage["completion_tokens"],
        "total_tokens": doc_usage["total_tokens"] + receipt_usage["total_tokens"],
    }

    return {
        "filename": filename,
        "document_intelligence": {
            "markdown": markdown,
        },
        "llm_analysis": {
            "document_summary": doc_summary.model_dump(exclude_none=True),
            "receipt_summary": receipt_summary,
        },
        "metrics": {
            "di_response_time_ms": di_elapsed_ms,
            "di_page_count": page_count,
            "llm_response_time_ms": llm_elapsed_ms,
            "llm_token_usage": total_usage,
            "llm_detail": {
                "document_summary_usage": doc_usage,
                "receipt_summary_usage": receipt_usage,
            },
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("web.app:app", host="0.0.0.0", port=8000, reload=True)
