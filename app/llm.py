"""
LLM helper — call Azure OpenAI chat completions to produce structured output.

Uses the Azure OpenAI SDK with Managed Identity authentication.
"""

from __future__ import annotations

import json
from typing import TypeVar

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from pydantic import BaseModel

from config import AZURE_OPENAI_ENDPOINT, LLM_DEPLOYMENT

T = TypeVar("T", bound=BaseModel)


def _make_strict_schema(schema: dict) -> dict:
    """Add 'additionalProperties': false and full 'required' for Azure OpenAI strict mode."""
    schema = schema.copy()
    if schema.get("type") == "object" or "properties" in schema:
        schema["additionalProperties"] = False
        if "properties" in schema:
            schema["required"] = list(schema["properties"].keys())
    if "properties" in schema:
        schema["properties"] = {
            k: _make_strict_schema(v) for k, v in schema["properties"].items()
        }
    if "items" in schema and isinstance(schema["items"], dict):
        schema["items"] = _make_strict_schema(schema["items"])
    if "$defs" in schema:
        schema["$defs"] = {
            k: _make_strict_schema(v) for k, v in schema["$defs"].items()
        }
    return schema


def _build_client() -> AzureOpenAI:
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default",
    )
    return AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        azure_ad_token_provider=token_provider,
        api_version="2025-04-01-preview",
    )


def extract_structured(
    raw_text: str,
    model_class: type[T],
    instruction: str = "Extract structured data from the following document content.",
) -> T:
    """Send raw extracted text to the LLM and return a validated Pydantic model."""
    client = _build_client()

    schema = _make_strict_schema(model_class.model_json_schema())

    response = client.chat.completions.create(
        model=LLM_DEPLOYMENT,
        messages=[
            {
                "role": "system",
                "content": (
                    f"{instruction}\n\n"
                    f"Respond with a JSON object that conforms to this schema:\n"
                    f"{json.dumps(schema, indent=2)}\n\n"
                    "All date values MUST use YYYY-MM-dd format (e.g. 2026-01-05).\n"
                    "All text values MUST be in Korean (한국어).\n"
                    "Return ONLY the JSON object, no explanation."
                ),
            },
            {"role": "user", "content": raw_text},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": model_class.__name__,
                "schema": schema,
                "strict": True,
            },
        },
        temperature=0.0,
    )

    content = response.choices[0].message.content
    return model_class.model_validate_json(content)


def pretty_print(obj: BaseModel) -> str:
    """Return a nicely formatted string of the Pydantic model."""
    return json.dumps(obj.model_dump(exclude_none=True), indent=2, ensure_ascii=False)
