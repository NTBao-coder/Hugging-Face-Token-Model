import re
import unicodedata

def normalize_text(text: str) -> str:
    """Normalize text by stripping surrounding whitespace, collapsing inner whitespace, and NFC normalisation."""
    if not text:
        return ""
    # NFC normalisation is critical for Vietnamese to compose accents properly
    text = unicodedata.normalize("NFC", text)
    # Collapse multiple whitespaces/newlines into a single space
    return re.sub(r"\s+", " ", text).strip()


def truncate_text(text: str, max_chars: int = 1500) -> str:
    """Truncate text to prevent overloading LLM or API token limits, adding ellipsis if truncated."""
    if not text:
        return ""
    normalized = normalize_text(text)
    if len(normalized) <= max_chars:
        return normalized
    return normalized[:max_chars] + "..."

def split_reviews(raw_text: str) -> list[str]:
    """Split review text by line, filtering out empty entries."""
    if not raw_text:
        return []
    return [normalize_text(line) for line in raw_text.splitlines() if line.strip()]
