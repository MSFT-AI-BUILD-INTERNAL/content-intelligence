"""
LLM helper — call Azure AI Foundry chat completions to produce structured output.

Uses the Foundry project endpoint with Managed Identity authentication.
"""

from __future__ import annotations

import json
from typing import TypeVar

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    JsonSchemaFormat,
    SystemMessage,
    UserMessage,
)
from pydantic import BaseModel

from auth import get_credential
from config import FOUNDRY_ENDPOINT, LLM_DEPLOYMENT

T = TypeVar("T", bound=BaseModel)


def _build_client() -> ChatCompletionsClient:
    return ChatCompletionsClient(
        endpoint=FOUNDRY_ENDPOINT,
        credential=get_credential(),
    )


def extract_structured(
    raw_text: str,
    model_class: type[T],
    instruction: str = "Extract structured data from the following document content.",
) -> T:
    """Send raw extracted text to the LLM and return a validated Pydantic model."""
    client = _build_client()

    schema = model_class.model_json_schema()

    response = client.complete(
        model=LLM_DEPLOYMENT,
        messages=[
            SystemMessage(
                content=(
                    f"{instruction}\n\n"
                    f"Respond with a JSON object that conforms to this schema:\n"
                    f"{json.dumps(schema, indent=2)}\n\n"
                    "Return ONLY the JSON object, no explanation."
                )
            ),
            UserMessage(content=raw_text),
        ],
        response_format=JsonSchemaFormat(
            name=model_class.__name__,
            schema=schema,
            strict=True,
        ),
        temperature=0.0,
    )

    content = response.choices[0].message.content
    return model_class.model_validate_json(content)


def pretty_print(obj: BaseModel) -> str:
    """Return a nicely formatted string of the Pydantic model."""
    return json.dumps(obj.model_dump(exclude_none=True), indent=2, ensure_ascii=False)
