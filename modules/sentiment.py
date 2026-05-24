"""Aspect-Based Sentiment Analysis and basic sentiment module."""

import re
from typing import Any
from modules import get_inference_client

# Define constants for rule-based fallback
ASPECT_KEYWORDS = {
    "dịch vụ": ["dịch vụ", "nhân viên", "phục vụ", "hướng dẫn viên", "lễ tân", "support", "staff", "service"],
    "vị trí": ["vị trí", "gần", "xa", "trung tâm", "biển", "sân bay", "di chuyển", "location", "near", "far"],
    "giá cả": ["giá", "chi phí", "đắt", "rẻ", "đáng tiền", "phí", "vé", "price", "cost", "expensive", "cheap", "value"],
    "tiện nghi": ["phòng", "wifi", "hồ bơi", "điều hòa", "giường", "view", "tiện nghi", "room", "pool", "bed", "ac"],
    "ẩm thực": ["đồ ăn", "bữa sáng", "nhà hàng", "món", "ăn uống", "cafe", "food", "breakfast", "restaurant"],
    "vệ sinh": ["sạch", "bẩn", "mùi", "vệ sinh", "gọn", "bụi", "clean", "dirty", "smell", "dusty"]
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

def rule_based_absa(text: str) -> list[dict[str, Any]]:
    """Perform rule-based aspect-based sentiment analysis as a fallback."""
    lowered = text.lower()
    results = []
    
    for aspect, keywords in ASPECT_KEYWORDS.items():
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
            "sentiment": sentiment,
            "confidence": round(confidence, 3),
            "source": "heuristic"
        })
    return results

def analyze_sentiment(text: str, mode: str = "basic") -> dict[str, Any] | list[dict[str, Any]]:
    """
    Analyze sentiment of travel text.
    
    mode="basic" -> returns dict {"label": "POSITIVE"|"NEGATIVE"|"NEUTRAL", "score": float}
    mode="absa"  -> returns list of dicts [{"aspect": str, "sentiment": str, "confidence": float, "source": str}]
    """
    client = get_inference_client()
    
    if mode == "basic":
        if client is None:
            # Fallback to local rule-based basic sentiment
            lowered = text.lower()
            pos_hits = [w for w in POSITIVE_WORDS if w in lowered]
            neg_hits = [w for w in NEGATIVE_WORDS if w in lowered]
            score_diff = len(pos_hits) - len(neg_hits)
            
            if score_diff > 0:
                return {"label": "POSITIVE", "score": 0.8, "source": "heuristic"}
            elif score_diff < 0:
                return {"label": "NEGATIVE", "score": 0.8, "source": "heuristic"}
            return {"label": "NEUTRAL", "score": 0.5, "source": "heuristic"}
            
        try:
            # Use twitter-roberta-base-sentiment-latest
            result = client.text_classification(
                text,
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            # Find label with highest score
            best = max(result, key=lambda x: x.score)
            label_map = {"positive": "POSITIVE", "negative": "NEGATIVE", "neutral": "NEUTRAL"}
            mapped_label = label_map.get(best.label.lower(), best.label.upper())
            return {"label": mapped_label, "score": round(best.score, 3), "source": "huggingface"}
        except Exception:
            # If API fails, use rule-based fallback
            lowered = text.lower()
            pos_hits = [w for w in POSITIVE_WORDS if w in lowered]
            neg_hits = [w for w in NEGATIVE_WORDS if w in lowered]
            score_diff = len(pos_hits) - len(neg_hits)
            
            if score_diff > 0:
                return {"label": "POSITIVE", "score": 0.75, "source": "heuristic_fallback"}
            elif score_diff < 0:
                return {"label": "NEGATIVE", "score": 0.75, "source": "heuristic_fallback"}
            return {"label": "NEUTRAL", "score": 0.5, "source": "heuristic_fallback"}
            
    elif mode == "absa":
        if client is None:
            return rule_based_absa(text)
            
        try:
            results = []
            # We check both English aspect list and Vietnamese aspect list
            # We can prompt the model: f"{review} [SEP] {aspect}"
            for aspect in TRAVEL_ASPECTS_EN:
                prompt = f"{text} [SEP] {aspect}"
                output = client.text_classification(
                    prompt,
                    model="yangheng/deberta-v3-base-absa-v1.1"
                )
                if output:
                    best = max(output, key=lambda x: x.score)
                    if best.score > 0.55:
                        results.append({
                            "aspect": aspect,
                            "sentiment": best.label.upper(),
                            "confidence": round(best.score, 3),
                            "source": "huggingface"
                        })
            
            # Map EN aspects to VI if the input is mostly Vietnamese
            is_vi = any(w in text.lower() for w in ["khách sạnh", "phòng", "vị trí", "ăn", "uống", "giá"])
            if is_vi and results:
                en_to_vi = {
                    "room": "tiện nghi",
                    "cleanliness": "vệ sinh",
                    "staff": "dịch vụ",
                    "service": "dịch vụ",
                    "location": "vị trí",
                    "food": "ẩm thực",
                    "price": "giá cả",
                    "wifi": "tiện nghi",
                    "pool": "tiện nghi"
                }
                mapped_results = []
                seen_aspects = set()
                for res in results:
                    vi_aspect = en_to_vi.get(res["aspect"], res["aspect"])
                    pair = (vi_aspect, res["sentiment"])
                    if pair not in seen_aspects:
                        seen_aspects.add(pair)
                        mapped_results.append({
                            "aspect": vi_aspect,
                            "sentiment": res["sentiment"],
                            "confidence": res["confidence"],
                            "source": "huggingface"
                        })
                results = mapped_results
                
            if not results:
                # If no aspect matches or scores are too low, fallback to rule-based ABSA
                return rule_based_absa(text)
            return results
        except Exception:
            return rule_based_absa(text)
            
    return {}
