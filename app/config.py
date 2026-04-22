"""Centralized configuration for Azure AI services."""

import os

from dotenv import load_dotenv

load_dotenv()

# Azure AI Foundry — Content Understanding (resource-level, no project path)
CONTENT_UNDERSTANDING_ENDPOINT = os.getenv(
    "CONTENT_UNDERSTANDING_ENDPOINT",
    "https://jinsungpark-westus-resource.services.ai.azure.com",
)

# Azure AI Foundry resource endpoint (v1 API — /openai/v1/ is appended in llm.py)
AZURE_OPENAI_ENDPOINT = os.getenv(
    "AZURE_OPENAI_ENDPOINT",
    "https://jinsang-foundry.services.ai.azure.com",
)

# LLM deployment name (used for structured output refinement)
LLM_DEPLOYMENT = os.getenv("LLM_DEPLOYMENT", "gpt-5.2-chat")

# Azure AI Document Intelligence
DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv(
    "DOCUMENT_INTELLIGENCE_ENDPOINT",
    "https://jinsungpark-westus-resource.cognitiveservices.azure.com/",
)
