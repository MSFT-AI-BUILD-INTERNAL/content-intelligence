"""Load prompt templates from prompts.yaml."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

_PROMPTS_PATH = Path(__file__).parent / "prompts.yaml"


@lru_cache(maxsize=1)
def _load() -> dict:
    with open(_PROMPTS_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_system_template() -> str:
    """Return the system prompt template with {instruction} and {schema} placeholders."""
    return _load()["system_template"]


def get_instruction(name: str) -> str:
    """Return a task-specific instruction by key name."""
    return _load()["instructions"][name]
