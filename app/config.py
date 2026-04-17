"""Centralized configuration for Azure AI services."""

import os

from dotenv import load_dotenv

load_dotenv()

# Azure AI Foundry — Content Understanding
FOUNDRY_ENDPOINT = os.getenv(
    "FOUNDRY_ENDPOINT",
    "https://jinsungpark-westus-resource.services.ai.azure.com/api/projects/jinsungpark-westus",
)

# Azure AI Document Intelligence
DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv(
    "DOCUMENT_INTELLIGENCE_ENDPOINT",
    "https://jinsungpark-westus-resource.cognitiveservices.azure.com/",
)
