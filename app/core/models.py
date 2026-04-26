"""Pydantic models for structured output."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DocumentSummary(BaseModel):
    title: str | None = Field(default=None, description="Document title or type")
    page_count: int = Field(description="Number of pages")
    language: str | None = Field(default=None, description="Primary language detected")
    summary: str = Field(description="Brief summary of the document content")
    key_phrases: list[str] = Field(default_factory=list, description="Key phrases or topics")
    tables_count: int = Field(default=0, description="Number of tables found")
