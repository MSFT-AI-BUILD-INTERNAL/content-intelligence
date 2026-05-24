"""
Content Understanding service — extract document content via Azure AI Foundry.

Uses the prebuilt-layout analyzer and returns structured markdown.
Authentication: Azure Managed Identity (DefaultAzureCredential).
"""

from __future__ import annotations

import mimetypes
from pathlib import Path

from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalysisResult,
    DocumentContent,
)

from core.auth import get_credential
from core.config import CONTENT_UNDERSTANDING_ENDPOINT


def _build_client() -> ContentUnderstandingClient:
    return ContentUnderstandingClient(
        endpoint=CONTENT_UNDERSTANDING_ENDPOINT,
        credential=get_credential(),
        credential_scopes=["https://ai.azure.com/.default"],
    )


def _extract_markdown(result: AnalysisResult) -> str:
    """Extract and join markdown parts from an analysis result."""
    parts: list[str] = []
    for content in result.contents:
        if isinstance(content, DocumentContent):
            parts.append(content.markdown)
    return "\n".join(parts)


def analyze_bytes(data: bytes, content_type: str) -> str:
    """Extract document content from raw bytes. Returns markdown."""
    client = _build_client()

    poller = client.begin_analyze_binary(
        analyzer_id="prebuilt-layout",
        binary_input=data,
        content_type=content_type,
    )
    return _extract_markdown(poller.result())


def analyze(file_path: Path) -> str:
    """Extract document content from a local file. Returns markdown."""
    guessed, _ = mimetypes.guess_type(file_path.name)
    content_type = guessed or "application/pdf"
    return analyze_bytes(file_path.read_bytes(), content_type)
