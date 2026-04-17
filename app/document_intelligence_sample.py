"""
Document Intelligence sample — analyze documents with Azure AI Document Intelligence.

Demonstrates:
  1. Layout analysis   (prebuilt-layout)
  2. Invoice analysis  (prebuilt-invoice)
  3. General document analysis (prebuilt-read)

All authentication goes through Azure Managed Identity (DefaultAzureCredential).
"""

from __future__ import annotations

import os

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

from auth import get_credential
from config import DOCUMENT_INTELLIGENCE_ENDPOINT


def _build_client() -> DocumentIntelligenceClient:
    return DocumentIntelligenceClient(
        endpoint=DOCUMENT_INTELLIGENCE_ENDPOINT,
        credential=get_credential(),
    )


# ------------------------------------------------------------------
# 1. Layout analysis (tables, paragraphs, selection marks)
# ------------------------------------------------------------------
def analyze_layout(file_path: str) -> None:
    """Extract layout information from a local document."""
    client = _build_client()

    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document(
            model_id="prebuilt-layout",
            body=f,
        )
    result = poller.result()

    print(f"[Document Intelligence — Layout] {file_path}")
    print(f"  Pages: {len(result.pages)}")
    for page in result.pages:
        print(f"  Page {page.page_number}: {page.width}x{page.height} ({page.unit})")
        if page.lines:
            print(f"    Lines: {len(page.lines)}")
    if result.tables:
        print(f"  Tables: {len(result.tables)}")
        for i, table in enumerate(result.tables, 1):
            print(f"    Table {i}: {table.row_count} rows x {table.column_count} cols")


# ------------------------------------------------------------------
# 2. Invoice analysis
# ------------------------------------------------------------------
def analyze_invoice(file_path: str) -> None:
    """Extract invoice fields from a local document."""
    client = _build_client()

    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document(
            model_id="prebuilt-invoice",
            body=f,
        )
    result = poller.result()

    print(f"[Document Intelligence — Invoice] {file_path}")
    if not result.documents:
        print("  No invoice data extracted.")
        return

    for doc in result.documents:
        print(f"  Doc type: {doc.doc_type}")
        if doc.fields:
            for name, field in doc.fields.items():
                value = field.get("valueString") or field.get("content", "")
                confidence = field.get("confidence", "N/A")
                print(f"    {name}: {value}  (confidence: {confidence})")


# ------------------------------------------------------------------
# 3. Read / OCR analysis
# ------------------------------------------------------------------
def analyze_read(file_path: str) -> None:
    """Extract text content using the prebuilt-read model (OCR)."""
    client = _build_client()

    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document(
            model_id="prebuilt-read",
            body=f,
        )
    result = poller.result()

    print(f"[Document Intelligence — Read/OCR] {file_path}")
    print(f"  Content (first 500 chars):\n{result.content[:500]}")
    print(f"  Pages: {len(result.pages)}")
    if result.languages:
        langs = [lang.locale for lang in result.languages]
        print(f"  Detected languages: {', '.join(langs)}")


# ------------------------------------------------------------------
# 4. Analyze from URL
# ------------------------------------------------------------------
def analyze_layout_from_url(url: str) -> None:
    """Extract layout from a publicly accessible URL."""
    client = _build_client()

    poller = client.begin_analyze_document(
        model_id="prebuilt-layout",
        body=AnalyzeDocumentRequest(url_source=url),
    )
    result = poller.result()

    print(f"[Document Intelligence — Layout from URL] {url}")
    print(f"  Pages: {len(result.pages)}")
    for page in result.pages:
        print(f"  Page {page.page_number}: {page.width}x{page.height} ({page.unit})")


# ------------------------------------------------------------------
# CLI entry
# ------------------------------------------------------------------
def main() -> None:
    sample_url = (
        "https://raw.githubusercontent.com/Azure-Samples/"
        "azure-ai-content-understanding-assets/main/document/invoice.pdf"
    )

    print("=" * 60)
    print("  Document Intelligence — Sample Runner")
    print("=" * 60)

    local_pdf = os.path.join(os.path.dirname(__file__), "sample_files", "sample.pdf")
    if os.path.exists(local_pdf):
        print("\n--- 1. Layout Analysis ---")
        analyze_layout(local_pdf)

        print("\n--- 2. Invoice Analysis ---")
        analyze_invoice(local_pdf)

        print("\n--- 3. Read / OCR Analysis ---")
        analyze_read(local_pdf)
    else:
        print(f"\n[SKIP] Local file not found: {local_pdf}")
        print("  Place a PDF in app/sample_files/sample.pdf to test local analysis.")

    print("\n--- 4. Layout Analysis from URL ---")
    analyze_layout_from_url(sample_url)


if __name__ == "__main__":
    main()
