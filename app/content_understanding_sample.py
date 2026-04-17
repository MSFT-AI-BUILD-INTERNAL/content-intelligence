"""
Content Understanding sample — analyze a receipt via Azure AI Foundry.

Analyzes sample_files/trip-receipt.pdf using prebuilt analyzers.
Authentication: Azure Managed Identity (DefaultAzureCredential).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import cast

from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalysisResult,
    ArrayField,
    DocumentContent,
    ObjectField,
)

from auth import get_credential
from config import FOUNDRY_ENDPOINT

SAMPLE_FILE = Path(__file__).parent / "sample_files" / "trip-receipt.pdf"


def _build_client() -> ContentUnderstandingClient:
    return ContentUnderstandingClient(
        endpoint=FOUNDRY_ENDPOINT,
        credential=get_credential(),
    )


def analyze_document(file_path: Path) -> AnalysisResult:
    """Extract document content with prebuilt-documentSearch."""
    client = _build_client()

    print(f"[Content Understanding] Analyzing: {file_path.name}")
    poller = client.begin_analyze_binary(
        analyzer_id="prebuilt-documentSearch",
        binary_input=file_path.read_bytes(),
    )
    result: AnalysisResult = poller.result()

    for content in result.contents:
        if isinstance(content, DocumentContent):
            print(f"  Pages: {content.start_page_number} – {content.end_page_number}")
            print(f"  Markdown preview (first 500 chars):\n{content.markdown[:500]}")
            if content.tables:
                print(f"  Tables found: {len(content.tables)}")
    return result


def analyze_receipt(file_path: Path) -> AnalysisResult:
    """Extract structured receipt fields with prebuilt-receipt."""
    client = _build_client()

    print(f"[Content Understanding] Analyzing receipt: {file_path.name}")
    poller = client.begin_analyze_binary(
        analyzer_id="prebuilt-receipt",
        binary_input=file_path.read_bytes(),
    )
    result: AnalysisResult = poller.result()

    if not result.contents:
        print("  No content returned.")
        return result

    doc = cast(DocumentContent, result.contents[0])
    if not doc.fields:
        print("  No fields extracted.")
        return result

    for field_name in ("MerchantName", "MerchantAddress", "TransactionDate"):
        field = doc.fields.get(field_name)
        if field:
            confidence = f" (confidence: {field.confidence:.2f})" if field.confidence else ""
            print(f"  {field_name}: {field.value}{confidence}")

    total = doc.fields.get("Total")
    if isinstance(total, ObjectField) and total.value:
        amount = total.value.get("Amount")
        currency = total.value.get("CurrencyCode")
        amt_str = f"{amount.value}" if amount else "N/A"
        cur_str = currency.value if currency and currency.value else ""
        print(f"  Total: {cur_str}{amt_str}")

    items = doc.fields.get("Items")
    if isinstance(items, ArrayField) and items.value:
        print(f"  Items ({len(items.value)}):")
        for i, item in enumerate(items.value, 1):
            if isinstance(item, ObjectField) and item.value:
                desc = item.value.get("Description")
                qty = item.value.get("Quantity")
                print(f"    [{i}] {desc.value if desc else 'N/A'}  x{qty.value if qty else '?'}")

    return result


def main() -> None:
    print("=" * 60)
    print("  Content Understanding — trip-receipt.pdf")
    print("=" * 60)

    if not SAMPLE_FILE.exists():
        print(f"\n[ERROR] File not found: {SAMPLE_FILE}")
        return

    print("\n--- 1. Document Analysis ---")
    analyze_document(SAMPLE_FILE)

    print("\n--- 2. Receipt Field Extraction ---")
    analyze_receipt(SAMPLE_FILE)


if __name__ == "__main__":
    main()
