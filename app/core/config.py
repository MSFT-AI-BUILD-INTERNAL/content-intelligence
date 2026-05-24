"""Centralized configuration for Azure AI services."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- Directory paths ---
APP_DIR = Path(__file__).resolve().parent.parent
SAMPLE_FILES_DIR = APP_DIR / "sample_files"
PROMPTS_FILE = APP_DIR / "core" / "prompts.yaml"

# --- Azure Blob Storage (web app file source) ---
BLOB_ACCOUNT_URL = os.getenv(
    "BLOB_ACCOUNT_URL", "https://jinsparkgen2.blob.core.windows.net"
)
BLOB_CONTAINER = os.getenv("BLOB_CONTAINER", "data")
BLOB_PREFIX = os.getenv("BLOB_PREFIX", "invoices/").rstrip("/") + "/"

# --- Azure AI Foundry — Content Understanding ---
CONTENT_UNDERSTANDING_ENDPOINT = os.getenv(
    "CONTENT_UNDERSTANDING_ENDPOINT",
    "https://jinsungpark-westus-resource.services.ai.azure.com",
)

# --- Azure AI Foundry — OpenAI (v1 API; /openai/v1/ is appended in llm.py) ---
AZURE_OPENAI_ENDPOINT = os.getenv(
    "AZURE_OPENAI_ENDPOINT",
    "https://jinsang-foundry.services.ai.azure.com",
)

# --- LLM deployment name ---
LLM_DEPLOYMENT = os.getenv("LLM_DEPLOYMENT", "gpt-5.2-chat")

# --- Azure AI Document Intelligence ---
DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv(
    "DOCUMENT_INTELLIGENCE_ENDPOINT",
    "https://jinsungpark-westus-resource.cognitiveservices.azure.com/",
)
