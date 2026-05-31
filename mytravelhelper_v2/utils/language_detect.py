from langdetect import detect_langs
import logging

class LanguageDetector:
    """Utility class to identify input language."""

    @staticmethod
    def detect(text: str) -> str:
        """
        Detect language code: 'vi' or 'en'.
        Defaults to 'en' if confidence is low or if exceptions occur.
        """
        if not text or not text.strip():
            return "en"

        # Heuristic word list check (very fast and robust for Vietnamese accents)
        vi_accented_chars = "áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ"
        if any(char in text.lower() for char in vi_accented_chars):
            return "vi"

        try:
            predictions = detect_langs(text)
            if predictions:
                best = predictions[0]
                if best.lang in ["vi", "en"]:
                    return best.lang
                # Map other similar langcodes if needed, or fallback
                return "vi" if best.lang == "zh-cn" or best.lang == "th" else "en"
        except Exception as e:
            logging.debug(f"Langdetect failed: {e}")

        # Final keyword heuristics
        vi_keywords = ["phòng", "khách", "sạn", "ở", "ăn", "uống", "giá", "ngon", "tệ", "sạch", "đẹp"]
        if any(w in text.lower() for w in vi_keywords):
            return "vi"

        return "en"
