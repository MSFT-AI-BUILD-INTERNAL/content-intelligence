"""
Web application for Document Intelligence + LLM analysis.

Run: uvicorn web.app:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from core.config import SAMPLE_FILES_DIR
from core.llm import extract_raw, extract_structured
from core.models import DocumentSummary
from core.prompts import get_instruction
from services.document_intelligence import analyze_layout, analyze_read, analyze_receipt

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

app = FastAPI(title="Content Intelligence Web")


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main HTML page."""
    html_path = TEMPLATES_DIR / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.get("/api/files")
async def list_files():
    """Return list of files in sample_files directory."""
    if not SAMPLE_FILES_DIR.exists():
        return {"files": []}
    files = sorted(
        f.name for f in SAMPLE_FILES_DIR.iterdir() if f.is_file() and not f.name.startswith(".")
    )
    return {"files": files}


@app.post("/api/analyze/{filename}")
async def analyze_file(filename: str):
    """Run Document Intelligence + LLM analysis on a file."""
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = SAMPLE_FILES_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    resolved = file_path.resolve()
    if not str(resolved).startswith(str(SAMPLE_FILES_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Invalid file path")

    # --- Document Intelligence ---
    layout_text = analyze_layout(file_path)
    ocr_text = analyze_read(file_path)
    receipt_text = analyze_receipt(file_path)

    di_result = {
        "layout": layout_text,
        "ocr_content": ocr_text,
        "receipt_fields": receipt_text,
    }

    # --- LLM Structured Output ---
    all_di_text = (
        f"=== Layout ===\n{layout_text}\n\n"
        f"=== OCR Full Text ===\n{ocr_text}\n\n"
        f"=== Receipt Fields ===\n{receipt_text}"
    )

    doc_summary = extract_structured(
        all_di_text,
        DocumentSummary,
        instruction=get_instruction("document_summary"),
    )

    receipt_summary = extract_raw(
        all_di_text,
        instruction=get_instruction("receipt_extraction"),
    )

    return {
        "filename": filename,
        "document_intelligence": di_result,
        "llm_analysis": {
            "document_summary": doc_summary.model_dump(exclude_none=True),
            "receipt_summary": receipt_summary,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("web.app:app", host="0.0.0.0", port=8000, reload=True)
