"""
Document Intelligence sample — analyze a receipt via Azure AI.

Analyzes sample_files/trip-receipt.pdf using the prebuilt-layout analyzer,
then refines the output into structured JSON via LLM.
"""

from __future__ import annotations

import json

from core.config import SAMPLE_FILES_DIR
from core.llm import extract_raw, extract_structured, pretty_print
from core.models import DocumentSummary
from core.prompts import get_instruction
from services.document_intelligence import analyze

SAMPLE_FILE = SAMPLE_FILES_DIR / "trip-receipt.pdf"


def main() -> None:
    print("=" * 60)
    print("  Document Intelligence — trip-receipt.pdf")
    print("=" * 60)

    if not SAMPLE_FILE.exists():
        print(f"\n[ERROR] File not found: {SAMPLE_FILE}")
        return

    # Extract markdown via Document Intelligence (single call)
    print("\n[Document Intelligence] Analyzing:", SAMPLE_FILE.name)
    markdown, page_count = analyze(SAMPLE_FILE)
    print(f"  Raw markdown extracted. ({page_count} pages)")

    # 1. Document analysis → structured summary via LLM
    print("\n--- 1. Document Analysis (structured) ---")
    print("  Sending to LLM for structuring...")
    doc_summary, _ = extract_structured(
        markdown,
        DocumentSummary,
        instruction=get_instruction("document_summary"),
    )
    print(pretty_print(doc_summary))

    # 2. Receipt field extraction via LLM (same markdown, different prompt)
    print("\n--- 2. Receipt Field Extraction (structured) ---")
    print("  Sending to LLM for structuring...")
    receipt, _ = extract_raw(
        markdown,
        instruction=get_instruction("receipt_extraction"),
    )
    print(json.dumps(receipt, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
