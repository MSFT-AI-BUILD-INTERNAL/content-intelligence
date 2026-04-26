"""
Content Understanding service — extract document content via Azure AI Foundry.

Uses the prebuilt-layout analyzer and returns structured markdown.
Authentication: Azure Managed Identity (DefaultAzureCredential).
"""

from __future__ import annotations

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


def analyze(file_path: Path) -> str:
    """Extract document content with prebuilt-layout. Returns markdown."""
    client = _build_client()

    poller = client.begin_analyze_binary(
        analyzer_id="prebuilt-layout",
        binary_input=file_path.read_bytes(),
        content_type="application/pdf",
    )
    result: AnalysisResult = poller.result()

    markdown_parts: list[str] = []
    for content in result.contents:
        if isinstance(content, DocumentContent):
            markdown_parts.append(content.markdown)

    return "\n".join(markdown_parts)
