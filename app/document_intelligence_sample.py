"""
Document Intelligence sample — analyze a receipt with Azure AI Document Intelligence.

Analyzes sample_files/trip-receipt.pdf using prebuilt models.
Authentication: Azure Managed Identity (DefaultAzureCredential).
"""

from __future__ import annotations

from pathlib import Path

from azure.ai.documentintelligence import DocumentIntelligenceClient

from auth import get_credential
from config import DOCUMENT_INTELLIGENCE_ENDPOINT

SAMPLE_FILE = Path(__file__).parent / "sample_files" / "trip-receipt.pdf"


def _build_client() -> DocumentIntelligenceClient:
    return DocumentIntelligenceClient(
        endpoint=DOCUMENT_INTELLIGENCE_ENDPOINT,
        credential=get_credential(),
    )


def analyze_layout(file_path: Path) -> None:
    """Extract layout information (tables, paragraphs, lines)."""
    client = _build_client()

    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document(model_id="prebuilt-layout", body=f)
    result = poller.result()

    print(f"[Document Intelligence — Layout] {file_path.name}")
    print(f"  Pages: {len(result.pages)}")
    for page in result.pages:
        print(f"  Page {page.page_number}: {page.width}x{page.height} ({page.unit})")
        if page.lines:
            print(f"    Lines: {len(page.lines)}")
    if result.tables:
        print(f"  Tables: {len(result.tables)}")
        for i, table in enumerate(result.tables, 1):
            print(f"    Table {i}: {table.row_count} rows x {table.column_count} cols")


def analyze_receipt(file_path: Path) -> None:
    """Extract receipt fields using the prebuilt-receipt model."""
    client = _build_client()

    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document(model_id="prebuilt-receipt", body=f)
    result = poller.result()

    print(f"[Document Intelligence — Receipt] {file_path.name}")
    if not result.documents:
        print("  No receipt data extracted.")
        return

    for doc in result.documents:
        print(f"  Doc type: {doc.doc_type}")
        if doc.fields:
            for name, field in doc.fields.items():
                value = field.get("valueString") or field.get("content", "")
                confidence = field.get("confidence", "N/A")
                print(f"    {name}: {value}  (confidence: {confidence})")


def analyze_read(file_path: Path) -> None:
    """Extract text content using the prebuilt-read model (OCR)."""
    client = _build_client()

    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document(model_id="prebuilt-read", body=f)
    result = poller.result()

    print(f"[Document Intelligence — Read/OCR] {file_path.name}")
    print(f"  Content (first 500 chars):\n{result.content[:500]}")
    print(f"  Pages: {len(result.pages)}")
    if result.languages:
        langs = [lang.locale for lang in result.languages]
        print(f"  Detected languages: {', '.join(langs)}")


def main() -> None:
    print("=" * 60)
    print("  Document Intelligence — trip-receipt.pdf")
    print("=" * 60)

    if not SAMPLE_FILE.exists():
        print(f"\n[ERROR] File not found: {SAMPLE_FILE}")
        return

    print("\n--- 1. Layout Analysis ---")
    analyze_layout(SAMPLE_FILE)

    print("\n--- 2. Receipt Analysis ---")
    analyze_receipt(SAMPLE_FILE)

    print("\n--- 3. Read / OCR Analysis ---")
    analyze_read(SAMPLE_FILE)


if __name__ == "__main__":
    main()
