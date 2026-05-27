"""Intent classification and Named Entity Recognition (NER) module."""

import re
from typing import Any
from modules import get_inference_client
from modules.translation import TranslationService, TranslationError
from utils.language_detect import LanguageDetector
from utils.label_mapper import map_entity_type, map_intent
from utils.preprocessing import normalize_vietnamese_text

# Travel intent mappings
TRAVEL_INTENTS = {
    "book hotel": "Đặt phòng khách sạn",
    "find restaurant": "Tìm nhà hàng",
    "get directions": "Hỏi đường / chỉ đường",
    "check weather": "Hỏi thời tiết",
    "find attraction": "Tìm điểm tham quan",
    "cancel booking": "Hủy đặt chỗ",
    "make complaint": "Phản ánh / khiếu nại",
    "request info": "Hỏi thông tin chung"
}

# Rule-based fallback keywords for intent
INTENT_KEYWORDS = {
    "book hotel": ["đặt phòng", "khách sạn", "vé", "booking", "đặt vé", "hotel", "book", "reservation"],
    "find restaurant": ["nhà hàng", "quán ăn", "ăn uống", "đặc sản", "món ăn", "restaurant", "food", "eat"],
    "get directions": ["đường", "chỉ đường", "bản đồ", "đi thế nào", "phương tiện", "directions", "map", "route"],
    "check weather": ["thời tiết", "mưa", "nắng", "nhiệt độ", "mùa nào", "bão", "weather", "rain", "temperature"],
    "find attraction": ["tham quan", "địa điểm", "chỗ chơi", "nổi tiếng", "đẹp", "attraction", "visit", "see", "sightseeing"],
    "cancel booking": ["hủy phòng", "hủy vé", "hủy đặt chỗ", "cancel", "refund"],
    "make complaint": ["tệ", "kém", "bẩn", "thất vọng", "khiếu nại", "phàn nàn", "complaint", "rude"],
    "request info": ["tư vấn", "thông tin", "gợi ý", "info", "guide", "recommend"]
}

KNOWN_PLACES = [
    "Hà Nội", "Sài Gòn", "TP.HCM", "Đà Nẵng", "Hội An", "Huế", "Đà Lạt", "Nha Trang", 
    "Phú Quốc", "Sapa", "Hạ Long", "Ninh Bình", "Cần Thơ", "Bangkok", "Singapore", "Seoul", "Tokyo",
    "Ha Noi", "Sai Gon", "Da Nang", "Hoi An", "Hue", "Da Lat", "Nha Trang", "Phu Quoc", "Ha Long", "Ninh Binh", "Can Tho"
]

def rule_based_intent(text: str) -> dict[str, Any]:
    """Fallback intent classifier using keyword heuristics."""
    lowered = text.lower()
    scores = {label: 0.0 for label in INTENT_KEYWORDS}
    
    for label, keywords in INTENT_KEYWORDS.items():
        # Count keyword occurrences
        match_count = sum(1.0 for kw in keywords if kw in lowered)
        scores[label] = match_count
        
    best_intent = max(scores, key=scores.get)
    max_score = scores[best_intent]
    
    if max_score == 0:
        return {"intent": "request info", "intent_vi": map_intent("request info"), "confidence": 0.5, "source": "heuristic"}
        
    confidence = 0.5 + min(0.45, max_score * 0.15)
    return {"intent": best_intent, "intent_vi": map_intent(best_intent), "confidence": round(confidence, 2), "source": "heuristic"}


def _prepare_english_input(text: str) -> dict[str, Any]:
    """Detect VI/EN and translate Vietnamese text before EN zero-shot/NER models."""
    normalized = normalize_vietnamese_text(text)
    translator = TranslationService()
    detection = LanguageDetector(translator).detect(normalized)
    translated = normalized

    if detection.language == "vi":
        try:
            translated = translator.translate(normalized, src="vi", dest="en")
        except TranslationError:
            translated = normalized

    return {
        "original_text": normalized,
        "text_for_model": translated,
        "translated_text": translated if translated != normalized else "",
        "detected_language": detection.language,
        "language_confidence": detection.confidence,
    }

def classify_intent(text: str, candidate_labels: list[str] | None = None) -> dict[str, Any]:
    """
    Classify the user intent into one of the travel categories.
    
    Returns a dict {"intent": str, "confidence": float, "source": str}
    """
    if not candidate_labels:
        candidate_labels = list(TRAVEL_INTENTS.keys())
        
    prepared = _prepare_english_input(text)
    text_for_model = prepared["text_for_model"]

    client = get_inference_client()
    if client is None:
        return {**rule_based_intent(text), **prepared}
        
    try:
        result = client.zero_shot_classification(
            text_for_model,
            candidate_labels,
            model="facebook/bart-large-mnli"
        )
        # Handle dict or classification output list
        if isinstance(result, dict):
            best_label = result["labels"][0]
            score = result["scores"][0]
        else:
            best_label = result[0].label
            score = result[0].score
            
        return {
            "intent": best_label,
            "intent_vi": map_intent(best_label),
            "confidence": round(score, 3),
            "source": "huggingface",
            **prepared,
        }
    except Exception:
        return {**rule_based_intent(text), **prepared}

def extract_entities(text: str) -> list[dict[str, Any]]:
    """
    Extract named entities (LOCATION, DATE, DURATION, BUDGET, etc.) using NER model and rules.
    
    Returns a list of dicts [{"word": str, "entity_type": str, "score": float, "start": int, "end": int, "source": str}]
    """
    entities = []
    prepared = _prepare_english_input(text)
    text_for_model = prepared["text_for_model"]
    
    # 1. Hugging Face NER extraction
    client = get_inference_client()
    if client is not None:
        try:
            hf_ents = client.token_classification(
                text_for_model,
                model="dslim/bert-base-NER",
                aggregation_strategy="simple"
            )
            for ent in hf_ents:
                word = getattr(ent, "word", None) or ent.get("word")
                etype = getattr(ent, "entity_group", None) or ent.get("entity_group")
                score = float(getattr(ent, "score", None) or ent.get("score", 0))
                start = int(getattr(ent, "start", None) or ent.get("start", -1))
                end = int(getattr(ent, "end", None) or ent.get("end", -1))
                
                # Map standard NER types
                mapped_type = etype
                if etype in ["LOC", "LOCATION"]:
                    mapped_type = "LOCATION"
                elif etype in ["PER", "PERSON"]:
                    mapped_type = "PERSON"
                elif etype in ["ORG", "ORGANIZATION"]:
                    mapped_type = "ORGANIZATION"
                    
                entities.append({
                    "word": word,
                    "entity_type": mapped_type,
                    "entity_type_vi": map_entity_type(mapped_type),
                    "score": round(score, 3),
                    "start": start,
                    "end": end,
                    "source": "huggingface_translated" if prepared["detected_language"] == "vi" else "huggingface",
                    "model_text": text_for_model,
                    "detected_language": prepared["detected_language"],
                })
        except Exception:
            pass # Fail silently, fall back to rules
            
    # 2. Rule-based location extraction (for known places)
    lowered = text.lower()
    for place in KNOWN_PLACES:
        # Use word boundaries or simple matching for cities
        pattern = r"\b" + re.escape(place.lower()) + r"\b"
        for match in re.finditer(pattern, lowered):
            start, end = match.span()
            # Avoid duplicating HF LOC
            if not any(e["entity_type"] == "LOCATION" and e["start"] <= start and e["end"] >= end for e in entities):
                entities.append({
                    "word": text[start:end],
                    "entity_type": "LOCATION",
                    "entity_type_vi": map_entity_type("LOCATION"),
                    "score": 1.0,
                    "start": start,
                    "end": end,
                    "source": "rules"
                })
                
    # 3. Rule-based date extraction
    date_patterns = [
        r"\bngày\s+\d{1,2}(?:[/-]\d{1,2}(?:[/-]\d{2,4})?|\s+tháng\s+\d{1,2})?(?:\s+năm\s+\d{4})?\b",
        r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b", # e.g. 12/20 or 20/12/2026
        r"\bnext\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|week|month)\b",
        r"\bthứ\s+[hai|ba|tư|năm|sáu|bảy|chủ nhật]+\s+tới\b"
    ]
    for pattern in date_patterns:
        for match in re.finditer(pattern, lowered):
            start, end = match.span()
            if not any(e["start"] <= start and e["end"] >= end for e in entities):
                entities.append({
                    "word": text[start:end],
                    "entity_type": "DATE",
                    "entity_type_vi": map_entity_type("DATE"),
                    "score": 0.95,
                    "start": start,
                    "end": end,
                    "source": "rules"
                })
                
    # 4. Rule-based duration extraction
    duration_patterns = [
        r"\b\d+\s*(?:ngày|đêm|tuần|tháng|hour|day|night|week|month)s?\b",
        r"\b\d+\s*days?\s*and\s*\d+\s*nights?\b"
    ]
    for pattern in duration_patterns:
        for match in re.finditer(pattern, lowered):
            start, end = match.span()
            if not any(e["start"] <= start and e["end"] >= end for e in entities):
                entities.append({
                    "word": text[start:end],
                    "entity_type": "DURATION",
                    "entity_type_vi": map_entity_type("DURATION"),
                    "score": 0.95,
                    "start": start,
                    "end": end,
                    "source": "rules"
                })
                
    # 5. Rule-based budget extraction
    budget_patterns = [
        r"\b\d+(?:[.,]\d+)?\s*(?:triệu|tr|k|vnd|đồng|đ|usd|\$)\b",
        r"\b\d+\s*million\s*(?:vnd|usd)?\b"
    ]
    for pattern in budget_patterns:
        for match in re.finditer(pattern, lowered):
            start, end = match.span()
            if not any(e["start"] <= start and e["end"] >= end for e in entities):
                entities.append({
                    "word": text[start:end],
                    "entity_type": "BUDGET",
                    "entity_type_vi": map_entity_type("BUDGET"),
                    "score": 0.95,
                    "start": start,
                    "end": end,
                    "source": "rules"
                })
                
    # Sort entities by start index
    entities.sort(key=lambda x: x["start"])
    return entities

def travel_chat(user_message: str) -> str:
    """Generate a travel-assistant response using a Hugging Face chat model."""
    client = get_inference_client()
    fallback = (
        "Gợi ý nhanh: Hãy xác định rõ điểm đến, thời gian chuyến đi, ngân sách dự kiến và phong cách du lịch của bạn. "
        f"Với câu hỏi '{user_message}', bạn có thể tham khảo lịch trình cơ bản 2 ngày 1 đêm, "
        "lựa chọn các địa điểm gần nhau để thuận tiện di chuyển, kết hợp thử các món ăn đặc sản địa phương."
    )
    if client is None:
        return fallback
        
    prompt = (
        "Bạn là MyTravelHelper, trợ lý du lịch nói tiếng Việt thông minh, nhiệt tình. "
        "Hãy trả lời người dùng ngắn gọn, thực tế, có cấu trúc rõ ràng (sử dụng gạch đầu dòng).\n\n"
        f"Người dùng hỏi: {user_message}\nTrợ lý trả lời:"
    )
    try:
        res = client.text_generation(
            prompt,
            model="mistralai/Mistral-7B-Instruct-v0.2",
            max_new_tokens=300,
            temperature=0.4,
            return_full_text=False
        )
        return res.strip()
    except Exception:
        return fallback
