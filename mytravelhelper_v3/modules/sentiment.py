"""Aspect-Based Sentiment Analysis and basic sentiment module with translation support."""

import re
import os
import json
from typing import Any, List, Dict
from modules import get_inference_client
from modules.translation import TranslationService
from utils.language_detect import LanguageDetector
from utils.label_mapper import LabelMapper

# Define constants for rule-based fallback (English keywords)
ASPECT_KEYWORDS_EN = {
    "room": ["room", "bed", "blanket", "pillow", "mattress", "furniture", "view", "balcony", "space"],
    "cleanliness": ["clean", "dirty", "smell", "dusty", "stain", "wash", "trash"],
    "staff": ["staff", "reception", "guard", "service", "cleaner", "host", "friendly", "helpful"],
    "service": ["service", "spa", "massage", "laundry", "airport transfer", "tour", "rental"],
    "location": ["location", "center", "near", "far", "convenient", "beach", "market", "airport"],
    "food": ["food", "breakfast", "buffet", "restaurant", "menu", "delicious", "drink"],
    "price": ["price", "cost", "expensive", "cheap", "value", "money", "fee"],
    "wifi": ["wifi", "network", "internet", "connection"],
    "pool": ["pool", "swimming pool"]
}

POSITIVE_WORDS = [
    "tốt", "tuyệt", "đẹp", "sạch", "thân thiện", "nhanh", "hài lòng", "đáng tiền", "dễ chịu", "ổn", "recommend",
    "good", "great", "excellent", "clean", "friendly", "fast", "satisfied", "nice", "love", "amazing"
]

NEGATIVE_WORDS = [
    "tệ", "xấu", "bẩn", "chậm", "đắt", "ồn", "thất vọng", "khó chịu", "xa", "kém", "không đáng", "ít", "cao",
    "bad", "terrible", "dirty", "slow", "expensive", "noisy", "disappointed", "poor", "far", "worst"
]

TRAVEL_ASPECTS_EN = ["room", "cleanliness", "staff", "service", "location", "food", "price", "wifi", "pool"]

def get_vietnamese_aspect_keywords() -> dict:
    """Load Vietnamese aspect keywords from config."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(os.path.dirname(current_dir), "config", "travel_aspects_vi.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Fallback
    return {
        "room": ["phòng", "giường", "chăn", "gối", "đệm", "bàn ghế", "view", "ban công"],
        "cleanliness": ["sạch", "bẩn", "vệ sinh", "mùi", "thơm", "dọn dẹp", "rác", "bụi"],
        "staff": ["nhân viên", "lễ tân", "bảo vệ", "phục vụ", "dọn phòng", "chủ nhà", "thái độ", "thân thiện"],
        "service": ["dịch vụ", "spa", "massage", "giặt là", "đón sân bay", "tour", "cho thuê xe"],
        "location": ["vị trí", "trung tâm", "gần", "xa", "tiện di chuyển", "biển", "chợ", "sân bay"],
        "food": ["đồ ăn", "bữa sáng", "buffet", "nhà hàng", "thực đơn", "món ăn", "ngon", "nước uống"],
        "price": ["giá", "chi phí", "đắt", "rẻ", "phù hợp", "tiền", "khuyến mãi", "phụ phí"],
        "wifi": ["wifi", "mạng", "internet", "kết nối", "sóng"],
        "pool": ["hồ bơi", "bể bơi", "pool"]
    }

def rule_based_absa(text: str, lang: str = "en") -> list[dict[str, Any]]:
    """Perform rule-based aspect-based sentiment analysis as a fallback."""
    lowered = text.lower()
    results = []
    
    # Load appropriate keywords based on language
    if lang == "vi":
        keywords_map = get_vietnamese_aspect_keywords()
    else:
        keywords_map = ASPECT_KEYWORDS_EN
        
    mapper = LabelMapper()
    
    for aspect, keywords in keywords_map.items():
        # Check if aspect is mentioned
        matched_keywords = [kw for kw in keywords if kw in lowered]
        if not matched_keywords:
            continue
            
        # Get sentences with keywords for local context
        sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
        snippets = [s.strip() for s in sentences if any(kw in s.lower() for kw in keywords)]
        context = " ".join(snippets).lower() if snippets else lowered
        
        pos_hits = [w for w in POSITIVE_WORDS if w in context]
        neg_hits = [w for w in NEGATIVE_WORDS if w in context]
        
        score_diff = len(pos_hits) - len(neg_hits)
        
        if score_diff > 0:
            sentiment = "POSITIVE"
            confidence = 0.7 + min(0.25, score_diff * 0.05)
        elif score_diff < 0:
            sentiment = "NEGATIVE"
            confidence = 0.7 + min(0.25, abs(score_diff) * 0.05)
        else:
            sentiment = "NEUTRAL"
            confidence = 0.5
            
        results.append({
            "aspect": aspect,
            "aspect_vi": mapper.map_aspect(aspect),
            "sentiment": sentiment,
            "sentiment_vi": mapper.map_sentiment(sentiment),
            "confidence": round(confidence, 3),
            "source": "heuristic"
        })
    return results

def analyze_sentiment(text: str, mode: str = "basic") -> dict[str, Any] | list[dict[str, Any]]:
    """
    Analyze sentiment of travel text (supports Vietnamese & English).
    """
    client = get_inference_client()
    mapper = LabelMapper()
    
    # 1. Detect language
    lang = LanguageDetector.detect(text)
    
    # 2. Translate if Vietnamese
    translated_text = text
    if lang == "vi":
        try:
            translator = TranslationService()
            translated_text = translator.translate(text, src="vi", dest="en")
        except Exception:
            pass
            
    if mode == "basic":
        if client is None:
            # Fallback to local rule-based basic sentiment on original text
            lowered = text.lower()
            pos_hits = [w for w in POSITIVE_WORDS if w in lowered]
            neg_hits = [w for w in NEGATIVE_WORDS if w in lowered]
            score_diff = len(pos_hits) - len(neg_hits)
            
            if score_diff > 0:
                lbl = "POSITIVE"
            elif score_diff < 0:
                lbl = "NEGATIVE"
            else:
                lbl = "NEUTRAL"
            return {
                "label": lbl,
                "label_vi": mapper.map_sentiment(lbl),
                "score": 0.8,
                "source": "heuristic",
                "original_text": text,
                "translated_text": translated_text if lang == "vi" else None
            }
            
        try:
            # Use twitter-roberta-base-sentiment-latest on English text
            result = client.text_classification(
                translated_text,
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            best = max(result, key=lambda x: x.score)
            label_map = {"positive": "POSITIVE", "negative": "NEGATIVE", "neutral": "NEUTRAL"}
            mapped_label = label_map.get(best.label.lower(), best.label.upper())
            
            return {
                "label": mapped_label,
                "label_vi": mapper.map_sentiment(mapped_label),
                "score": round(best.score, 3),
                "source": "huggingface",
                "original_text": text,
                "translated_text": translated_text if lang == "vi" else None
            }
        except Exception:
            # If API fails, use rule-based fallback
            lowered = text.lower()
            pos_hits = [w for w in POSITIVE_WORDS if w in lowered]
            neg_hits = [w for w in NEGATIVE_WORDS if w in lowered]
            score_diff = len(pos_hits) - len(neg_hits)
            
            if score_diff > 0:
                lbl = "POSITIVE"
            elif score_diff < 0:
                lbl = "NEGATIVE"
            else:
                lbl = "NEUTRAL"
            return {
                "label": lbl,
                "label_vi": mapper.map_sentiment(lbl),
                "score": 0.75,
                "source": "heuristic_fallback",
                "original_text": text,
                "translated_text": translated_text if lang == "vi" else None
            }
            
    elif mode == "absa":
        if client is None:
            return rule_based_absa(text, lang=lang)
            
        try:
            results = []
            # Query DeBERTa ABSA using English prompts
            for aspect in TRAVEL_ASPECTS_EN:
                prompt = f"{translated_text} [SEP] {aspect}"
                output = client.text_classification(
                    prompt,
                    model="yangheng/deberta-v3-base-absa-v1.1"
                )
                if output:
                    best = max(output, key=lambda x: x.score)
                    if best.score > 0.55:
                        results.append({
                            "aspect": aspect,
                            "aspect_vi": mapper.map_aspect(aspect),
                            "sentiment": best.label.upper(),
                            "sentiment_vi": mapper.map_sentiment(best.label.upper()),
                            "confidence": round(best.score, 3),
                            "source": "huggingface"
                        })
            
            if not results:
                # If no aspect matches, fallback to rule-based ABSA
                return rule_based_absa(text, lang=lang)
            return results
        except Exception:
            return rule_based_absa(text, lang=lang)
            
    return {}
