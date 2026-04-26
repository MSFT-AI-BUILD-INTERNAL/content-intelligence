"""
Document Intelligence sample — analyze a receipt with Azure AI Document Intelligence.

Analyzes sample_files/trip-receipt.pdf using prebuilt models,
then refines the output into structured JSON via LLM.
"""

from __future__ import annotations

import json

from core.config import SAMPLE_FILES_DIR
from core.llm import extract_raw, extract_structured, pretty_print
from core.models import DocumentSummary
from core.prompts import get_instruction
from services.document_intelligence import analyze_layout, analyze_read, analyze_receipt

SAMPLE_FILE = SAMPLE_FILES_DIR / "trip-receipt.pdf"


def main() -> None:
    print("=" * 60)
    print("  Document Intelligence — trip-receipt.pdf")
    print("=" * 60)

    if not SAMPLE_FILE.exists():
        print(f"\n[ERROR] File not found: {SAMPLE_FILE}")
        return

    # 1. Layout + OCR → structured document summary via LLM
    print("\n--- 1. Document Analysis (structured) ---")
    print(f"[Document Intelligence] Analyzing layout: {SAMPLE_FILE.name}")
    layout_text = analyze_layout(SAMPLE_FILE)
    print(f"[Document Intelligence] Running OCR: {SAMPLE_FILE.name}")
    ocr_text = analyze_read(SAMPLE_FILE)

    combined = f"=== Layout ===\n{layout_text}\n\n=== OCR Content ===\n{ocr_text}"
    print("  Raw data extracted. Sending to LLM for structuring...")

    doc_summary = extract_structured(
        combined,
        DocumentSummary,
        instruction=get_instruction("document_summary"),
    )
    print(pretty_print(doc_summary))

    # 2. Receipt analysis → structured receipt via LLM
    print("\n--- 2. Receipt Analysis (structured) ---")
    print(f"[Document Intelligence] Analyzing receipt: {SAMPLE_FILE.name}")
    receipt_text = analyze_receipt(SAMPLE_FILE)
    print("  Raw receipt data extracted. Sending to LLM for structuring...")

    receipt = extract_raw(
        receipt_text,
        instruction=get_instruction("receipt_extraction"),
    )
    print(json.dumps(receipt, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
