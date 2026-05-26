"""Language detection helpers for Vietnamese/English travel input."""

from __future__ import annotations

from dataclasses import dataclass

from modules.translation import TranslationService


@dataclass(frozen=True)
class LanguageDetectionResult:
    language: str
    confidence: float
    source: str


class LanguageDetector:
    """Small VI/EN detector with heuristic-first behavior for offline reliability."""

    VI_CHARS = set("ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ")
    VI_WORDS = (
        "phòng",
        "khách sạn",
        "nhân viên",
        "dịch vụ",
        "đặt",
        "hủy",
        "thời tiết",
        "địa điểm",
        "đường đi",
        "ngân sách",
        "triệu",
        "đêm",
    )

    def __init__(self, translator: TranslationService | None = None):
        self.translator = translator or TranslationService()

    def detect(self, text: str) -> LanguageDetectionResult:
        if not text or not text.strip():
            return LanguageDetectionResult("en", 0.0, "empty")

        lowered = text.lower()
        if any(char in lowered for char in self.VI_CHARS):
            return LanguageDetectionResult("vi", 0.98, "heuristic")
        if any(word in lowered for word in self.VI_WORDS):
            return LanguageDetectionResult("vi", 0.85, "heuristic")

        lang, confidence = self.translator.detect_language(text)
        lang = "vi" if lang == "vi" else "en"
        return LanguageDetectionResult(lang, confidence, "translator")

    def is_vietnamese(self, text: str) -> bool:
        return self.detect(text).language == "vi"

