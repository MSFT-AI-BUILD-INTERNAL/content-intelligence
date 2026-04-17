"""Centralized configuration for Azure AI services."""

import os

from dotenv import load_dotenv

load_dotenv()

# Azure AI Foundry — Content Understanding (resource-level, no project path)
CONTENT_UNDERSTANDING_ENDPOINT = os.getenv(
    "CONTENT_UNDERSTANDING_ENDPOINT",
    "https://jinsungpark-westus-resource.services.ai.azure.com",
)

# Azure OpenAI endpoint (cognitiveservices, used for LLM chat completions)
AZURE_OPENAI_ENDPOINT = os.getenv(
    "AZURE_OPENAI_ENDPOINT",
    "https://jinsungpark-westus-resource.cognitiveservices.azure.com",
)

# LLM deployment name (used for structured output refinement)
LLM_DEPLOYMENT = os.getenv("LLM_DEPLOYMENT", "gpt-4-1-mini")

# Azure AI Document Intelligence
DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv(
    "DOCUMENT_INTELLIGENCE_ENDPOINT",
    "https://jinsungpark-westus-resource.cognitiveservices.azure.com/",
)
