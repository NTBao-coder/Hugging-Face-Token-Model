"""Intent classification and Named Entity Recognition (NER) module with translation support."""

import re
import unicodedata
from typing import Any, List, Dict
from modules import get_inference_client
from modules.translation import TranslationService
from utils.language_detect import LanguageDetector
from utils.label_mapper import LabelMapper

# Travel intent mappings (fallback values)
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

# Rule-based fallback keywords for intent (supports both EN and VI)
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

def align_entity(ent_word: str, original_text: str) -> dict | None:
    """Align a translated English entity word back to the original Vietnamese text."""
    # 1. Direct match (case-insensitive)
    pattern = r'\b' + re.escape(ent_word.lower()) + r'\b'
    match = re.search(pattern, original_text.lower())
    if match:
        start, end = match.span()
        return {"word": original_text[start:end], "start": start, "end": end}
    
    # 2. Translate back to Vietnamese and search
    try:
        translator = TranslationService()
        ent_vi = translator.translate(ent_word, src="en", dest="vi")
        pattern_vi = r'\b' + re.escape(ent_vi.lower()) + r'\b'
        match_vi = re.search(pattern_vi, original_text.lower())
        if match_vi:
            start, end = match_vi.span()
            return {"word": original_text[start:end], "start": start, "end": end}
    except Exception:
        pass
    
    # 3. Match without accents (diacritics removal)
    def strip_accents(text):
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    
    clean_original = strip_accents(original_text.lower())
    clean_ent = strip_accents(ent_word.lower())
    
    match_clean = re.search(r'\b' + re.escape(clean_ent) + r'\b', clean_original)
    if match_clean:
        start, end = match_clean.span()
        return {"word": original_text[start:end], "start": start, "end": end}
        
    try:
        clean_ent_vi = strip_accents(ent_vi.lower())
        match_clean_vi = re.search(r'\b' + re.escape(clean_ent_vi) + r'\b', clean_original)
        if match_clean_vi:
            start, end = match_clean_vi.span()
            return {"word": original_text[start:end], "start": start, "end": end}
    except Exception:
        pass
        
    return None

def rule_based_intent(text: str) -> dict[str, Any]:
    """Fallback intent classifier using keyword heuristics."""
    lowered = text.lower()
    scores = {label: 0.0 for label in INTENT_KEYWORDS}
    
    for label, keywords in INTENT_KEYWORDS.items():
        match_count = sum(1.0 for kw in keywords if kw in lowered)
        scores[label] = match_count
        
    best_intent = max(scores, key=scores.get)
    max_score = scores[best_intent]
    
    mapper = LabelMapper()
    
    if max_score == 0:
        lbl = "request info"
        return {
            "intent": lbl,
            "intent_vi": mapper.map_intent(lbl),
            "confidence": 0.5,
            "source": "heuristic"
        }
        
    confidence = 0.5 + min(0.45, max_score * 0.15)
    return {
        "intent": best_intent,
        "intent_vi": mapper.map_intent(best_intent),
        "confidence": round(confidence, 2),
        "source": "heuristic"
    }

def classify_intent(text: str, candidate_labels: list[str] | None = None) -> dict[str, Any]:
    """
    Classify the user intent into one of the travel categories (supports translation).
    """
    if not candidate_labels:
        candidate_labels = list(TRAVEL_INTENTS.keys())
        
    client = get_inference_client()
    mapper = LabelMapper()
    
    # 1. Detect language
    lang = LanguageDetector.detect(text)
    
    # 2. Translate to English if Vietnamese
    translated_text = text
    if lang == "vi":
        try:
            translator = TranslationService()
            translated_text = translator.translate(text, src="vi", dest="en")
        except Exception:
            pass
            
    if client is None:
        return rule_based_intent(text)
        
    try:
        result = client.zero_shot_classification(
            translated_text,
            candidate_labels,
            model="facebook/bart-large-mnli"
        )
        if isinstance(result, dict):
            best_label = result["labels"][0]
            score = result["scores"][0]
        else:
            best_label = result[0].label
            score = result[0].score
            
        return {
            "intent": best_label,
            "intent_vi": mapper.map_intent(best_label),
            "confidence": round(score, 3),
            "source": "huggingface",
            "original_text": text,
            "translated_text": translated_text if lang == "vi" else None
        }
    except Exception:
        return rule_based_intent(text)

def extract_entities(text: str) -> list[dict[str, Any]]:
    """
    Extract named entities (LOCATION, DATE, DURATION, BUDGET, etc.) using NER model and rules.
    If text is Vietnamese, it translates to English first to execute standard NER model,
    then aligns findings back to the original text.
    """
    entities = []
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
            
    # 3. Hugging Face NER extraction on English/translated text
    client = get_inference_client()
    if client is not None:
        try:
            hf_ents = client.token_classification(
                translated_text,
                model="dslim/bert-base-NER",
                aggregation_strategy="simple"
            )
            for ent in hf_ents:
                word = getattr(ent, "word", None) or ent.get("word")
                etype = getattr(ent, "entity_group", None) or ent.get("entity_group")
                score = float(getattr(ent, "score", None) or ent.get("score", 0))
                start = int(getattr(ent, "start", None) or ent.get("start", -1))
                end = int(getattr(ent, "end", None) or ent.get("end", -1))
                
                mapped_type = etype
                if etype in ["LOC", "LOCATION"]:
                    mapped_type = "LOCATION"
                elif etype in ["PER", "PERSON"]:
                    mapped_type = "PERSON"
                elif etype in ["ORG", "ORGANIZATION"]:
                    mapped_type = "ORGANIZATION"
                
                # If original was Vietnamese, we align the word back to Vietnamese
                aligned_word = word
                aligned_start = start
                aligned_end = end
                
                if lang == "vi" and word:
                    alignment = align_entity(word, text)
                    if alignment:
                        aligned_word = alignment["word"]
                        aligned_start = alignment["start"]
                        aligned_end = alignment["end"]
                        
                entities.append({
                    "word": aligned_word,
                    "entity_type": mapped_type,
                    "entity_type_vi": mapper.map_entity_type(mapped_type),
                    "score": round(score, 3),
                    "start": aligned_start,
                    "end": aligned_end,
                    "source": "huggingface"
                })
        except Exception:
            pass
            
    # 4. Rule-based location extraction directly on original text
    lowered = text.lower()
    for place in KNOWN_PLACES:
        pattern = r"\b" + re.escape(place.lower()) + r"\b"
        for match in re.finditer(pattern, lowered):
            start, end = match.span()
            if not any(e["entity_type"] == "LOCATION" and e["start"] <= start and e["end"] >= end for e in entities):
                entities.append({
                    "word": text[start:end],
                    "entity_type": "LOCATION",
                    "entity_type_vi": mapper.map_entity_type("LOCATION"),
                    "score": 1.0,
                    "start": start,
                    "end": end,
                    "source": "rules"
                })
                
    # 5. Rule-based date extraction directly on original text
    date_patterns = [
        r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b",
        r"\bngày\s+\d{1,2}(?:\s+tháng\s+\d{1,2})?(?:\s+năm\s+\d{4})?\b",
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
                    "entity_type_vi": mapper.map_entity_type("DATE"),
                    "score": 0.95,
                    "start": start,
                    "end": end,
                    "source": "rules"
                })
                
    # 6. Rule-based duration extraction directly on original text
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
                    "entity_type_vi": mapper.map_entity_type("DURATION"),
                    "score": 0.95,
                    "start": start,
                    "end": end,
                    "source": "rules"
                })
                
    # 7. Rule-based budget extraction directly on original text
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
                    "entity_type_vi": mapper.map_entity_type("BUDGET"),
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
    
    # 1. Detect language
    lang = LanguageDetector.detect(user_message)
    
    # 2. Translate if VI
    translated_message = user_message
    if lang == "vi":
        try:
            translator = TranslationService()
            translated_message = translator.translate(user_message, src="vi", dest="en")
        except Exception:
            pass
            
    fallback_en = (
        "Quick tip: Please specify your destination, duration, budget, and travel style. "
        "For your question, you can consider a basic 2-day 1-night itinerary, "
        "selecting attractions close to each other for easy transportation, and tasting local foods."
    )
    fallback_vi = (
        "Gợi ý nhanh: Hãy xác định rõ điểm đến, thời gian chuyến đi, ngân sách dự kiến và phong cách du lịch của bạn. "
        f"Với câu hỏi '{user_message}', bạn có thể tham khảo lịch trình cơ bản 2 ngày 1 đêm, "
        "lựa chọn các địa điểm gần nhau để thuận tiện di chuyển, kết hợp thử các món ăn đặc sản địa phương."
    )
    
    if client is None:
        return fallback_vi if lang == "vi" else fallback_en
        
    prompt = (
        "You are MyTravelHelper, a smart and enthusiastic travel assistant. "
        "Please answer the user query in a structured, concise way (using bullet points).\n\n"
        f"User asks: {translated_message}\nAssistant answers:"
    )
    
    try:
        res = client.text_generation(
            prompt,
            model="mistralai/Mistral-7B-Instruct-v0.2",
            max_new_tokens=300,
            temperature=0.4,
            return_full_text=False
        )
        ans_en = res.strip()
        
        # 3. Translate answer back to VI if original query was VI
        if lang == "vi":
            translator = TranslationService()
            return translator.translate(ans_en, src="en", dest="vi")
        return ans_en
    except Exception:
        return fallback_vi if lang == "vi" else fallback_en


