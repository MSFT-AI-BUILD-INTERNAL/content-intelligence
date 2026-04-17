"""
Document Intelligence sample — analyze a receipt with Azure AI Document Intelligence.

Analyzes sample_files/trip-receipt.pdf using prebuilt models,
then refines the output into structured JSON via LLM.
Authentication: Azure Managed Identity (DefaultAzureCredential).
"""

from __future__ import annotations

from pathlib import Path

from azure.ai.documentintelligence import DocumentIntelligenceClient

from auth import get_credential
from config import DOCUMENT_INTELLIGENCE_ENDPOINT
from llm import extract_structured, pretty_print
from models import DocumentSummary, ReceiptSummary

SAMPLE_FILE = Path(__file__).parent / "sample_files" / "trip-receipt.pdf"


def _build_client() -> DocumentIntelligenceClient:
    return DocumentIntelligenceClient(
        endpoint=DOCUMENT_INTELLIGENCE_ENDPOINT,
        credential=get_credential(),
    )


def analyze_layout(file_path: Path) -> str:
    """Extract layout information and return as text."""
    client = _build_client()

    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document(model_id="prebuilt-layout", body=f)
    result = poller.result()

    lines: list[str] = []
    lines.append(f"Pages: {len(result.pages)}")
    for page in result.pages:
        lines.append(f"Page {page.page_number}: {page.width}x{page.height} ({page.unit})")
        if page.lines:
            for line in page.lines:
                lines.append(line.content)
    if result.tables:
        lines.append(f"Tables: {len(result.tables)}")
        for i, table in enumerate(result.tables, 1):
            lines.append(f"Table {i}: {table.row_count} rows x {table.column_count} cols")

    return "\n".join(lines)


def analyze_receipt(file_path: Path) -> str:
    """Extract receipt fields and return as text."""
    client = _build_client()

    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document(model_id="prebuilt-receipt", body=f)
    result = poller.result()

    lines: list[str] = []
    if result.documents:
        for doc in result.documents:
            lines.append(f"Doc type: {doc.doc_type}")
            if doc.fields:
                for name, field in doc.fields.items():
                    value = field.get("valueString") or field.get("content", "")
                    confidence = field.get("confidence", "N/A")
                    lines.append(f"{name}: {value} (confidence: {confidence})")

    return "\n".join(lines)


def analyze_read(file_path: Path) -> str:
    """Extract text content using OCR. Returns full content."""
    client = _build_client()

    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document(model_id="prebuilt-read", body=f)
    result = poller.result()

    return result.content


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
        instruction="Summarize this document. Extract title, language, key phrases, and a brief summary.",
    )
    print(pretty_print(doc_summary))

    # 2. Receipt analysis → structured receipt via LLM
    print("\n--- 2. Receipt Analysis (structured) ---")
    print(f"[Document Intelligence] Analyzing receipt: {SAMPLE_FILE.name}")
    receipt_text = analyze_receipt(SAMPLE_FILE)
    print("  Raw receipt data extracted. Sending to LLM for structuring...")

    receipt = extract_structured(
        receipt_text,
        ReceiptSummary,
        instruction="Extract structured receipt information including merchant, items, and totals.",
    )
    print(pretty_print(receipt))


if __name__ == "__main__":
    main()
