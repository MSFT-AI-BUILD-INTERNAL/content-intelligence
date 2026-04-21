"""
Web application for Document Intelligence + LLM analysis.

Run: uvicorn webapp:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from document_intelligence_sample import analyze_layout, analyze_read, analyze_receipt
from llm import extract_raw, extract_structured
from models import DocumentSummary
from prompts import get_instruction

SAMPLE_DIR = Path(__file__).parent / "sample_files"

app = FastAPI(title="Content Intelligence Web")


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main HTML page."""
    html_path = Path(__file__).parent / "templates" / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.get("/api/files")
async def list_files():
    """Return list of files in sample_files directory."""
    if not SAMPLE_DIR.exists():
        return {"files": []}
    files = sorted(
        f.name for f in SAMPLE_DIR.iterdir() if f.is_file() and not f.name.startswith(".")
    )
    return {"files": files}


@app.post("/api/analyze/{filename}")
async def analyze_file(filename: str):
    """Run Document Intelligence + LLM analysis on a file."""
    # Prevent path traversal
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = SAMPLE_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Resolve to ensure it's still inside SAMPLE_DIR
    resolved = file_path.resolve()
    if not str(resolved).startswith(str(SAMPLE_DIR.resolve())):
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

    # Receipt: send all DI data so LLM can extract every detail
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
