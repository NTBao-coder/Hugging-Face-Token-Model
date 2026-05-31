import os
from typing import Literal, List, Tuple
import logging

class TranslationService:
    """
    Unified translation service wrapper.
    Supports backend: 'googletrans' (default), 'google_cloud' (optional), and fallback via 'deep_translator'.
    """
    def __init__(self, backend: Literal["googletrans", "google_cloud"] = "googletrans"):
        self.backend = backend
        self._client = None
        self._init_client()

    def _init_client(self):
        if self.backend == "googletrans":
            try:
                from googletrans import Translator
                self._client = Translator()
            except ImportError:
                logging.warning("googletrans is not installed. Will use fallback.")
        elif self.backend == "google_cloud":
            try:
                from google.cloud import translate_v2 as translate
                self._client = translate.Client()
            except Exception as e:
                logging.error(f"Failed to initialize Google Cloud Translate Client: {e}. Falling back to googletrans.")
                self.backend = "googletrans"
                try:
                    from googletrans import Translator
                    self._client = Translator()
                except ImportError:
                    pass

    def translate(self, text: str, src: str = "vi", dest: str = "en") -> str:
        """Translate text. Returns translated string."""
        if not text or not text.strip():
            return text
        
        # 1. Primary backend
        try:
            if self.backend == "googletrans" and self._client is not None:
                # googletrans works with 'vi' and 'en'
                result = self._client.translate(text, src=src, dest=dest)
                if result and result.text:
                    return result.text
            elif self.backend == "google_cloud" and self._client is not None:
                result = self._client.translate(text, source_language=src, target_language=dest)
                if result and "translatedText" in result:
                    # Clear html entity escapes like &#39; if any
                    import html
                    return html.unescape(result["translatedText"])
        except Exception as e:
            logging.warning(f"Primary translator backend failed: {e}. Attempting fallback...")

        # 2. Fallback backend using deep-translator
        try:
            from deep_translator import GoogleTranslator
            fallback_translator = GoogleTranslator(source=src, target=dest)
            translated = fallback_translator.translate(text)
            if translated:
                return translated
        except Exception as e_fallback:
            logging.error(f"Fallback translation also failed: {e_fallback}")
        
        return text  # final fallback: return original text

    def detect_language(self, text: str) -> Tuple[str, float]:
        """Detect language. Returns (language_code, confidence)."""
        if not text or not text.strip():
            return "en", 1.0

        try:
            if self.backend == "googletrans" and self._client is not None:
                detected = self._client.detect(text)
                return detected.lang, detected.confidence
            elif self.backend == "google_cloud" and self._client is not None:
                result = self._client.detect_language(text)
                return result["language"], result["confidence"]
        except Exception as e:
            logging.warning(f"Primary language detection failed: {e}")

        # Fallback to langdetect
        try:
            from langdetect import detect_langs
            predictions = detect_langs(text)
            if predictions:
                best = predictions[0]
                return best.lang, best.prob
        except Exception:
            pass

        # Simplistic heuristic fallback
        is_vi = any(w in text.lower() for w in ["phòng", "khách", "sạn", "đẹp", "tệ", "sạch", "ăn", "uống", "giá", "ngon"])
        return ("vi", 0.9) if is_vi else ("en", 0.9)

    def batch_translate(self, texts: List[str], src: str = "vi", dest: str = "en") -> List[str]:
        """Translate a batch of texts."""
        if not texts:
            return []
        
        if self.backend == "google_cloud" and self._client is not None:
            try:
                import html
                results = self._client.translate(texts, source_language=src, target_language=dest)
                return [html.unescape(r["translatedText"]) for r in results]
            except Exception as e:
                logging.warning(f"Batch translate with GCP failed: {e}")
        
        # Loop translate with fallback cache/batching
        translated_list = []
        for text in texts:
            translated_list.append(self.translate(text, src, dest))
        return translated_list
