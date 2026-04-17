"""Pydantic models for structured receipt analysis output."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReceiptItem(BaseModel):
    description: str = Field(description="Item description")
    quantity: float | None = Field(default=None, description="Item quantity")
    unit_price: float | None = Field(default=None, description="Unit price")
    total_price: float | None = Field(default=None, description="Total price for this item")


class ReceiptSummary(BaseModel):
    merchant_name: str | None = Field(default=None, description="Merchant / store name")
    merchant_address: str | None = Field(default=None, description="Merchant address")
    transaction_date: str | None = Field(default=None, description="Transaction date (ISO 8601)")
    currency: str | None = Field(default=None, description="Currency code (e.g. USD, KRW)")
    subtotal: float | None = Field(default=None, description="Subtotal before tax")
    tax: float | None = Field(default=None, description="Tax amount")
    total: float | None = Field(default=None, description="Total amount")
    items: list[ReceiptItem] = Field(default_factory=list, description="Line items")


class DocumentSummary(BaseModel):
    title: str | None = Field(default=None, description="Document title or type")
    page_count: int = Field(description="Number of pages")
    language: str | None = Field(default=None, description="Primary language detected")
    summary: str = Field(description="Brief summary of the document content")
    key_phrases: list[str] = Field(default_factory=list, description="Key phrases or topics")
    tables_count: int = Field(default=0, description="Number of tables found")
