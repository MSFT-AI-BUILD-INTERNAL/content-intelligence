"""
Document Intelligence service — extract document content via Azure AI.

Uses prebuilt models (layout, read, receipt) and returns structured text.
Authentication: Azure Managed Identity (DefaultAzureCredential).
"""

from __future__ import annotations

import json
import mimetypes
from pathlib import Path

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, DocumentContentFormat

from core.auth import get_credential
from core.config import DOCUMENT_INTELLIGENCE_ENDPOINT


def _build_client() -> DocumentIntelligenceClient:
    return DocumentIntelligenceClient(
        endpoint=DOCUMENT_INTELLIGENCE_ENDPOINT,
        credential=get_credential(),
    )


def analyze_bytes(data: bytes, content_type: str) -> tuple[str, int]:
    """Extract document content from raw bytes using prebuilt-layout. Returns (markdown, page_count)."""
    import base64

    client = _build_client()

    base64_source = base64.b64encode(data).decode("utf-8")
    poller = client.begin_analyze_document(
        model_id="prebuilt-layout",
        body=AnalyzeDocumentRequest(bytes_source=base64_source),
        output_content_format=DocumentContentFormat.MARKDOWN,
    )
    result = poller.result()
    page_count = len(result.pages) if result.pages else 0
    return result.content, page_count


def analyze(file_path: Path) -> tuple[str, int]:
    """Extract document content from a local file. Returns (markdown, page_count)."""
    guessed, _ = mimetypes.guess_type(file_path.name)
    content_type = guessed or "application/pdf"
    return analyze_bytes(file_path.read_bytes(), content_type)


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


def _serialize_field(field, indent: int = 0) -> str:
    """Recursively serialize a Document Intelligence field to readable text."""
    prefix = "  " * indent

    if not isinstance(field, dict):
        return str(field)

    field_type = field.get("type", "")

    # Array field (e.g. Items)
    if field_type == "array" and "valueArray" in field:
        parts: list[str] = []
        for i, item in enumerate(field["valueArray"], 1):
            parts.append(f"{prefix}[{i}]")
            parts.append(_serialize_field(item, indent + 1))
        return "\n".join(parts)

    # Object field (e.g. each Item in Items)
    if field_type == "object" and "valueObject" in field:
        parts = []
        for key, sub_field in field["valueObject"].items():
            parts.append(f"{prefix}{key}: {_serialize_field(sub_field, indent)}")
        return "\n".join(parts)

    # Scalar fields
    for value_key in ("valueString", "valueNumber", "valueInteger",
                      "valueDate", "valueTime", "valueCurrencyAmount",
                      "valuePhoneNumber", "valueCountryRegion",
                      "valueSelectionMark", "valueSignature",
                      "valueAddress", "valueBoolean"):
        val = field.get(value_key)
        if val is not None:
            if value_key == "valueCurrencyAmount" and isinstance(val, dict):
                amount = val.get("amount", "")
                code = val.get("currencyCode", "")
                return f"{code} {amount}" if code else str(amount)
            if value_key == "valueAddress" and isinstance(val, dict):
                addr_parts = [
                    val.get("streetAddress", ""),
                    val.get("city", ""),
                    val.get("state", ""),
                    val.get("postalCode", ""),
                    val.get("countryRegion", ""),
                ]
                return ", ".join(p for p in addr_parts if p)
            if isinstance(val, dict):
                return json.dumps(val, ensure_ascii=False)
            if isinstance(val, list):
                return ", ".join(str(v) for v in val)
            return str(val)

    content = field.get("content", "")
    if content:
        return str(content)

    return json.dumps(field, ensure_ascii=False, default=str)


def analyze_receipt(file_path: Path) -> str:
    """Extract receipt fields and return as text with full nested detail."""
    client = _build_client()

    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document(model_id="prebuilt-receipt", body=f)
    result = poller.result()

    lines: list[str] = []
    if result.documents:
        for doc in result.documents:
            lines.append(f"Doc type: {doc.doc_type}")
            confidence = getattr(doc, "confidence", None)
            if confidence is not None:
                lines.append(f"Confidence: {confidence}")
            if doc.fields:
                for name, field in doc.fields.items():
                    serialized = _serialize_field(field)
                    field_conf = field.get("confidence", "")
                    conf_str = f" (confidence: {field_conf})" if field_conf else ""
                    lines.append(f"{name}: {serialized}{conf_str}")

    return "\n".join(lines)


def analyze_read(file_path: Path) -> str:
    """Extract text content using OCR. Returns full content."""
    client = _build_client()

    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document(model_id="prebuilt-read", body=f)
    result = poller.result()

    return result.content
