"""Translation layer for MyTravelHelper multilingual processing."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal


LanguageCode = Literal["auto", "en", "vi"]
TranslationBackend = Literal["auto", "googletrans", "google_cloud", "mock"]


MOCK_TRANSLATIONS = {
    ("vi", "en"): {
        "phòng sạch": "clean room",
        "nhân viên thân thiện": "friendly staff",
        "phòng rất sạch": "the room is very clean",
        "dịch vụ tệ": "bad service",
        "vị trí đẹp": "beautiful location",
        "giá hợp lý": "reasonable price",
    },
    ("en", "vi"): {
        "clean room": "phòng sạch",
        "friendly staff": "nhân viên thân thiện",
        "the room is very clean": "phòng rất sạch",
        "bad service": "dịch vụ tệ",
        "beautiful location": "vị trí đẹp",
        "reasonable price": "giá hợp lý",
    },
}


class TranslationError(Exception):
    """Raised when all configured translation backends fail."""


class TranslationService:
    """Unified Google Translate wrapper with a safe offline fallback.

    Backends:
    - ``googletrans``: demo-friendly, no key required.
    - ``google_cloud``: production option via Google Cloud credentials.
    - ``mock``: tiny deterministic fallback for offline demos/tests.
    """

    def __init__(self, backend: TranslationBackend = "auto"):
        self.backend = self._resolve_backend(backend)
        self._client = None
        self._init_client()

    def _resolve_backend(self, backend: TranslationBackend) -> TranslationBackend:
        if backend != "auto":
            return backend
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GOOGLE_TRANSLATE_API_KEY"):
            return "google_cloud"
        return "googletrans"

    def _init_client(self) -> None:
        if self.backend == "googletrans":
            try:
                from googletrans import Translator

                self._client = Translator()
            except Exception:
                self.backend = "mock"
                self._client = None
        elif self.backend == "google_cloud":
            try:
                from google.cloud import translate_v2

                self._client = translate_v2.Client()
            except Exception:
                self.backend = "googletrans"
                self._init_client()

    @lru_cache(maxsize=512)
    def translate(self, text: str, src: LanguageCode = "auto", dest: LanguageCode = "en") -> str:
        """Translate a single text string."""
        if not text or not text.strip() or src == dest:
            return text

        try:
            if self.backend == "googletrans" and self._client is not None:
                result = self._client.translate(text, src=src, dest=dest)
                return result.text

            if self.backend == "google_cloud" and self._client is not None:
                kwargs = {"target_language": dest}
                if src != "auto":
                    kwargs["source_language"] = src
                result = self._client.translate(text, **kwargs)
                return result["translatedText"]

            return self._mock_translate(text, src=src, dest=dest)
        except Exception as exc:
            mock = self._mock_translate(text, src=src, dest=dest)
            if mock != text:
                return mock
            raise TranslationError(f"Translation failed: {exc}") from exc

    def detect_language(self, text: str) -> tuple[str, float]:
        """Return a best-effort ``(language_code, confidence)`` pair."""
        if not text or not text.strip():
            return "en", 0.0

        if self.backend == "googletrans" and self._client is not None:
            try:
                detected = self._client.detect(text)
                return detected.lang, float(detected.confidence or 0.0)
            except Exception:
                pass

        if self.backend == "google_cloud" and self._client is not None:
            try:
                result = self._client.detect_language(text)
                return result["language"], float(result.get("confidence", 0.0))
            except Exception:
                pass

        return self._heuristic_detect(text)

    def batch_translate(
        self,
        texts: list[str],
        src: LanguageCode = "auto",
        dest: LanguageCode = "en",
    ) -> list[str]:
        """Translate a list of strings, preserving order."""
        if not texts:
            return []

        if self.backend == "google_cloud" and self._client is not None:
            try:
                kwargs = {"target_language": dest}
                if src != "auto":
                    kwargs["source_language"] = src
                results = self._client.translate(texts, **kwargs)
                return [item["translatedText"] for item in results]
            except Exception:
                pass

        return [self.translate(text, src=src, dest=dest) for text in texts]

    def _mock_translate(self, text: str, src: LanguageCode, dest: LanguageCode) -> str:
        source = "vi" if src == "auto" else src
        lookup = MOCK_TRANSLATIONS.get((source, dest), {})
        lowered = text.strip().lower()
        for phrase, translated in lookup.items():
            if phrase in lowered:
                return lowered.replace(phrase, translated)
        return text

    def _heuristic_detect(self, text: str) -> tuple[str, float]:
        vietnamese_markers = "ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ"
        lowered = text.lower()
        if any(char in lowered for char in vietnamese_markers):
            return "vi", 0.95
        vi_words = ["phòng", "khách sạn", "nhân viên", "đặt", "hủy", "thời tiết", "địa điểm"]
        if any(word in lowered for word in vi_words):
            return "vi", 0.8
        return "en", 0.7

