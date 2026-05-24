"""
Azure Blob Storage service — list and download files for the web app.

Replaces local sample_files/ directory with remote blob storage.
Authentication: Azure Managed Identity (DefaultAzureCredential).
"""

from __future__ import annotations

import mimetypes
import posixpath

from azure.storage.blob import BlobServiceClient

from core.auth import get_credential
from core.config import BLOB_ACCOUNT_URL, BLOB_CONTAINER, BLOB_PREFIX

# Content types supported by Azure AI Content Understanding
_SUPPORTED_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/tiff",
    "image/bmp",
}


def _build_client() -> BlobServiceClient:
    return BlobServiceClient(
        account_url=BLOB_ACCOUNT_URL,
        credential=get_credential(),
    )


def list_files() -> list[str]:
    """List file names under the configured blob prefix."""
    client = _build_client()
    container = client.get_container_client(BLOB_CONTAINER)

    names: list[str] = []
    for blob in container.list_blobs(name_starts_with=BLOB_PREFIX):
        # Skip the prefix directory marker itself
        rel = blob.name[len(BLOB_PREFIX) :]
        if rel and "/" not in rel and not rel.startswith("."):
            names.append(rel)

    return sorted(names)


def download_file(filename: str) -> tuple[bytes, str]:
    """Download a blob and return (data, content_type).

    Raises ``FileNotFoundError`` if the blob does not exist.
    Raises ``ValueError`` if the content type is not supported.
    """
    blob_name = posixpath.join(BLOB_PREFIX, filename)

    client = _build_client()
    blob_client = client.get_blob_client(BLOB_CONTAINER, blob_name)

    if not blob_client.exists():
        raise FileNotFoundError(f"Blob not found: {blob_name}")

    props = blob_client.get_blob_properties()
    content_type = props.content_settings.content_type or ""

    # Fallback: guess from extension if blob has no content type or generic one
    if not content_type or content_type == "application/octet-stream":
        guessed, _ = mimetypes.guess_type(filename)
        content_type = guessed or "application/octet-stream"

    if content_type not in _SUPPORTED_TYPES:
        raise ValueError(
            f"Unsupported content type '{content_type}' for '{filename}'. "
            f"Supported: {', '.join(sorted(_SUPPORTED_TYPES))}"
        )

    data = blob_client.download_blob().readall()
    return data, content_type
