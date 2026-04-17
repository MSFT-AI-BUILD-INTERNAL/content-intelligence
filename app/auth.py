"""
Shared authentication helper — Azure Managed Identity only.

Uses DefaultAzureCredential which automatically picks up:
  - System/User-assigned Managed Identity (when deployed on Azure)
  - Azure CLI / VS Code credentials (for local development)

API keys are intentionally NOT supported.
"""

from azure.identity import DefaultAzureCredential


def get_credential() -> DefaultAzureCredential:
    """Return a DefaultAzureCredential instance for Managed Identity auth."""
    return DefaultAzureCredential()
