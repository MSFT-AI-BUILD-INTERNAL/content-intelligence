"""
Content Understanding sample — analyze a receipt via Azure AI Foundry.

Analyzes sample_files/trip-receipt.pdf using prebuilt analyzers,
then refines the output into structured JSON via LLM.
Authentication: Azure Managed Identity (DefaultAzureCredential).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalysisResult,
    DocumentContent,
)

from auth import get_credential
from config import CONTENT_UNDERSTANDING_ENDPOINT
from llm import extract_raw, extract_structured, pretty_print
from models import DocumentSummary
from prompts import get_instruction

SAMPLE_FILE = Path(__file__).parent / "sample_files" / "trip-receipt.pdf"


def _build_client() -> ContentUnderstandingClient:
    return ContentUnderstandingClient(
        endpoint=CONTENT_UNDERSTANDING_ENDPOINT,
        credential=get_credential(),
        credential_scopes=["https://ai.azure.com/.default"],
    )


def analyze_document(file_path: Path) -> str:
    """Extract document content with prebuilt-documentSearch. Returns markdown."""
    client = _build_client()

    print(f"[Content Understanding] Analyzing: {file_path.name}")
    poller = client.begin_analyze_binary(
        analyzer_id="prebuilt-documentSearch",
        binary_input=file_path.read_bytes(),
    )
    result: AnalysisResult = poller.result()

    markdown_parts: list[str] = []
    for content in result.contents:
        if isinstance(content, DocumentContent):
            markdown_parts.append(content.markdown)

    return "\n".join(markdown_parts)


def analyze_receipt(file_path: Path) -> str:
    """Extract receipt content with prebuilt-receipt. Returns raw text."""
    client = _build_client()

    print(f"[Content Understanding] Analyzing receipt: {file_path.name}")
    poller = client.begin_analyze_binary(
        analyzer_id="prebuilt-receipt",
        binary_input=file_path.read_bytes(),
    )
    result: AnalysisResult = poller.result()

    parts: list[str] = []
    for content in result.contents:
        if isinstance(content, DocumentContent):
            parts.append(content.markdown)
            if content.fields:
                for name, field in content.fields.items():
                    parts.append(f"{name}: {field.value} (confidence: {field.confidence})")

    return "\n".join(parts)


def main() -> None:
    print("=" * 60)
    print("  Content Understanding — trip-receipt.pdf")
    print("=" * 60)

    if not SAMPLE_FILE.exists():
        print(f"\n[ERROR] File not found: {SAMPLE_FILE}")
        return

    # 1. Document analysis → structured summary via LLM
    print("\n--- 1. Document Analysis (structured) ---")
    markdown = analyze_document(SAMPLE_FILE)
    print("  Raw markdown extracted. Sending to LLM for structuring...")

    doc_summary = extract_structured(
        markdown,
        DocumentSummary,
        instruction=get_instruction("document_summary"),
    )
    print(pretty_print(doc_summary))

    # 2. Receipt analysis → structured receipt via LLM
    print("\n--- 2. Receipt Field Extraction (structured) ---")
    receipt_text = analyze_receipt(SAMPLE_FILE)
    print("  Raw receipt data extracted. Sending to LLM for structuring...")

    receipt = extract_raw(
        receipt_text,
        instruction=get_instruction("receipt_extraction"),
    )
    print(json.dumps(receipt, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
