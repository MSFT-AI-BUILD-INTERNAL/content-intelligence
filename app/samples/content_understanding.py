"""
Content Understanding sample — analyze a receipt via Azure AI Foundry.

Analyzes sample_files/trip-receipt.pdf using the prebuilt-layout analyzer,
then refines the output into structured JSON via LLM.
"""

from __future__ import annotations

import json

from core.config import SAMPLE_FILES_DIR
from core.llm import extract_raw, extract_structured, pretty_print
from core.models import DocumentSummary
from core.prompts import get_instruction
from services.content_understanding import analyze

SAMPLE_FILE = SAMPLE_FILES_DIR / "trip-receipt.pdf"


def main() -> None:
    print("=" * 60)
    print("  Content Understanding — trip-receipt.pdf")
    print("=" * 60)

    if not SAMPLE_FILE.exists():
        print(f"\n[ERROR] File not found: {SAMPLE_FILE}")
        return

    # Extract markdown via Content Understanding (single call)
    print("\n[Content Understanding] Analyzing:", SAMPLE_FILE.name)
    markdown = analyze(SAMPLE_FILE)
    print("  Raw markdown extracted.")

    # 1. Document analysis → structured summary via LLM
    print("\n--- 1. Document Analysis (structured) ---")
    print("  Sending to LLM for structuring...")
    doc_summary = extract_structured(
        markdown,
        DocumentSummary,
        instruction=get_instruction("document_summary"),
    )
    print(pretty_print(doc_summary))

    # 2. Receipt field extraction via LLM (same markdown, different prompt)
    print("\n--- 2. Receipt Field Extraction (structured) ---")
    print("  Sending to LLM for structuring...")
    receipt = extract_raw(
        markdown,
        instruction=get_instruction("receipt_extraction"),
    )
    print(json.dumps(receipt, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
