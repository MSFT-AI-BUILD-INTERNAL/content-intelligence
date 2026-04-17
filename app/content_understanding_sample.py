"""
Content Understanding sample — analyze documents & images via Azure AI Foundry.

Demonstrates:
  1. Analyze a local PDF file (binary upload)
  2. Analyze a document from a public URL
  3. Analyze an invoice and extract structured fields

All authentication goes through Azure Managed Identity (DefaultAzureCredential).
"""

from __future__ import annotations

import os
from typing import cast

from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalysisInput,
    AnalysisResult,
    ArrayField,
    DocumentContent,
    ObjectField,
)

from auth import get_credential
from config import FOUNDRY_ENDPOINT


def _build_client() -> ContentUnderstandingClient:
    return ContentUnderstandingClient(
        endpoint=FOUNDRY_ENDPOINT,
        credential=get_credential(),
    )


# ------------------------------------------------------------------
# 1. Analyze a local PDF (binary)
# ------------------------------------------------------------------
def analyze_local_document(file_path: str) -> AnalysisResult:
    """Upload a local document and extract content with prebuilt-documentSearch."""
    client = _build_client()

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    print(f"[Content Understanding] Analyzing local file: {file_path}")
    poller = client.begin_analyze_binary(
        analyzer_id="prebuilt-documentSearch",
        binary_input=file_bytes,
    )
    result: AnalysisResult = poller.result()

    for content in result.contents:
        if isinstance(content, DocumentContent):
            print(f"  Pages: {content.start_page_number} – {content.end_page_number}")
            print(f"  Markdown preview (first 500 chars):\n{content.markdown[:500]}")
            if content.tables:
                print(f"  Tables found: {len(content.tables)}")
    return result


# ------------------------------------------------------------------
# 2. Analyze a document from URL
# ------------------------------------------------------------------
def analyze_document_from_url(url: str) -> AnalysisResult:
    """Analyze a remote document using prebuilt-documentSearch."""
    client = _build_client()

    print(f"[Content Understanding] Analyzing URL: {url}")
    poller = client.begin_analyze(
        analyzer_id="prebuilt-documentSearch",
        inputs=[AnalysisInput(url=url)],
    )
    result: AnalysisResult = poller.result()

    for content in result.contents:
        if isinstance(content, DocumentContent):
            print(f"  Pages: {content.start_page_number} – {content.end_page_number}")
            print(f"  Markdown preview (first 500 chars):\n{content.markdown[:500]}")
    return result


# ------------------------------------------------------------------
# 3. Analyze an invoice and extract structured fields
# ------------------------------------------------------------------
def analyze_invoice(url: str) -> AnalysisResult:
    """Analyze an invoice and extract structured fields (prebuilt-invoice)."""
    client = _build_client()

    print(f"[Content Understanding] Analyzing invoice: {url}")
    poller = client.begin_analyze(
        analyzer_id="prebuilt-invoice",
        inputs=[AnalysisInput(url=url)],
    )
    result: AnalysisResult = poller.result()

    if not result.contents:
        print("  No content returned.")
        return result

    doc = cast(DocumentContent, result.contents[0])
    if not doc.fields:
        print("  No fields extracted.")
        return result

    # Print key invoice fields
    for field_name in ("CustomerName", "VendorName", "InvoiceDate", "InvoiceId"):
        field = doc.fields.get(field_name)
        if field:
            confidence = f" (confidence: {field.confidence:.2f})" if field.confidence else ""
            print(f"  {field_name}: {field.value}{confidence}")

    # Total amount (nested object)
    total = doc.fields.get("TotalAmount")
    if isinstance(total, ObjectField) and total.value:
        amount = total.value.get("Amount")
        currency = total.value.get("CurrencyCode")
        amt_str = f"{amount.value}" if amount else "N/A"
        cur_str = currency.value if currency and currency.value else ""
        print(f"  TotalAmount: {cur_str}{amt_str}")

    # Line items (array)
    items = doc.fields.get("LineItems")
    if isinstance(items, ArrayField) and items.value:
        print(f"  LineItems ({len(items.value)}):")
        for i, item in enumerate(items.value, 1):
            if isinstance(item, ObjectField) and item.value:
                desc = item.value.get("Description")
                qty = item.value.get("Quantity")
                print(f"    [{i}] {desc.value if desc else 'N/A'}  x{qty.value if qty else '?'}")

    return result


# ------------------------------------------------------------------
# CLI entry
# ------------------------------------------------------------------
def main() -> None:
    sample_url = (
        "https://raw.githubusercontent.com/Azure-Samples/"
        "azure-ai-content-understanding-assets/main/document/invoice.pdf"
    )

    print("=" * 60)
    print("  Content Understanding — Sample Runner")
    print("=" * 60)

    # Local file analysis (if a sample file exists)
    local_pdf = os.path.join(os.path.dirname(__file__), "sample_files", "sample.pdf")
    if os.path.exists(local_pdf):
        print("\n--- 1. Local Document Analysis ---")
        analyze_local_document(local_pdf)
    else:
        print(f"\n[SKIP] Local file not found: {local_pdf}")
        print("  Place a PDF in app/sample_files/sample.pdf to test local analysis.")

    # URL-based analysis
    print("\n--- 2. URL Document Analysis ---")
    analyze_document_from_url(sample_url)

    # Invoice analysis
    print("\n--- 3. Invoice Field Extraction ---")
    analyze_invoice(sample_url)


if __name__ == "__main__":
    main()
