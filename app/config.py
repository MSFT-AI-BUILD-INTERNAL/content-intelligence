"""Centralized configuration for Azure AI services."""

import os

from dotenv import load_dotenv

load_dotenv()

# Azure AI Foundry — Content Understanding & LLM
FOUNDRY_ENDPOINT = os.getenv(
    "FOUNDRY_ENDPOINT",
    "https://jinsungpark-westus-resource.services.ai.azure.com/api/projects/jinsungpark-westus",
)

# LLM deployment name (used for structured output refinement)
LLM_DEPLOYMENT = os.getenv("LLM_DEPLOYMENT", "gpt-4o")

# Azure AI Document Intelligence
DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv(
    "DOCUMENT_INTELLIGENCE_ENDPOINT",
    "https://jinsungpark-westus-resource.cognitiveservices.azure.com/",
)
