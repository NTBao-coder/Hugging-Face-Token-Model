"""Utility helpers for configuration and text preparation."""

from __future__ import annotations

import os
import re
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency is installed from requirements.txt.
    load_dotenv = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_environment() -> None:
    """Load local .env values when the file exists."""
    if load_dotenv is not None:
        load_dotenv(PROJECT_ROOT / ".env")


def get_hf_token() -> str | None:
    """Read a Hugging Face token from common environment variable names."""
    load_environment()
    return os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")


def has_hf_token() -> bool:
    return bool(get_hf_token())


def normalize_text(text: str) -> str:
    """Collapse whitespace while preserving Vietnamese accents."""
    return re.sub(r"\s+", " ", text or "").strip()


def split_reviews(raw_text: str) -> list[str]:
    """Split user-provided reviews by line while ignoring empty entries."""
    return [line.strip() for line in raw_text.splitlines() if line.strip()]


def pipeline_mermaid() -> str:
    return """
flowchart LR
    A[Streamlit Input] --> B[Intent + Entity Extraction]
    B --> C{Routing}
    C --> D[LLM Travel Chat]
    C --> E[Aspect Sentiment]
    C --> F[Topic Detection]
    D --> G[Streamlit Output]
    E --> G
    F --> G
"""
