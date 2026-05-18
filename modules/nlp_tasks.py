"""NLP tasks for intent filtering, entity extraction, ABSA and topic detection."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from modules.utils import normalize_text


INTENT_LABELS = [
    "travel_chat",
    "destination_information",
    "itinerary_planning",
    "review_analysis",
    "budget_question",
    "weather_question",
    "booking_support",
]

INTENT_KEYWORDS = {
    "itinerary_planning": ["lịch trình", "kế hoạch", "đi mấy ngày", "tour", "ngày 1", "ngày 2"],
    "destination_information": ["ở đâu", "địa điểm", "tham quan", "nổi tiếng", "có gì"],
    "review_analysis": ["review", "đánh giá", "phân tích", "cảm xúc", "nhận xét"],
    "budget_question": ["chi phí", "ngân sách", "giá", "bao nhiêu tiền", "rẻ"],
    "weather_question": ["thời tiết", "mưa", "nắng", "nhiệt độ", "mùa nào"],
    "booking_support": ["đặt phòng", "khách sạn", "vé", "booking", "đặt vé"],
    "travel_chat": ["xin chào", "hello", "tư vấn", "gợi ý"],
}

KNOWN_PLACES = [
    "Hà Nội",
    "Sài Gòn",
    "TP.HCM",
    "Đà Nẵng",
    "Hội An",
    "Huế",
    "Đà Lạt",
    "Nha Trang",
    "Phú Quốc",
    "Sapa",
    "Hạ Long",
    "Ninh Bình",
    "Cần Thơ",
    "Bangkok",
    "Singapore",
    "Seoul",
    "Tokyo",
]

ASPECT_KEYWORDS = {
    "Dịch vụ": ["dịch vụ", "nhân viên", "phục vụ", "hướng dẫn viên", "lễ tân", "support"],
    "Vị trí": ["vị trí", "gần", "xa", "trung tâm", "biển", "sân bay", "di chuyển"],
    "Giá cả": ["giá", "chi phí", "đắt", "rẻ", "đáng tiền", "phí", "vé"],
    "Tiện nghi": ["phòng", "wifi", "hồ bơi", "điều hòa", "giường", "view", "tiện nghi"],
    "Ẩm thực": ["đồ ăn", "bữa sáng", "nhà hàng", "món", "ăn uống", "cafe"],
    "Vệ sinh": ["sạch", "bẩn", "mùi", "vệ sinh", "gọn", "bụi"],
}

POSITIVE_WORDS = [
    "tốt",
    "tuyệt",
    "đẹp",
    "sạch",
    "thân thiện",
    "nhanh",
    "hài lòng",
    "đáng tiền",
    "dễ chịu",
    "ổn",
    "recommend",
]

NEGATIVE_WORDS = [
    "tệ",
    "xấu",
    "bẩn",
    "chậm",
    "đắt",
    "ồn",
    "thất vọng",
    "khó chịu",
    "xa",
    "kém",
    "không đáng",
    "ít",
    "cao",
]

TOPIC_KEYWORDS = {
    "Biển và nghỉ dưỡng": ["biển", "resort", "hồ bơi", "view", "nắng", "đảo"],
    "Ẩm thực địa phương": ["đồ ăn", "món", "nhà hàng", "chợ", "hải sản", "bữa sáng"],
    "Di chuyển": ["taxi", "xe", "sân bay", "đi bộ", "di chuyển", "kẹt xe", "gần"],
    "Lưu trú": ["khách sạn", "phòng", "homestay", "giường", "lễ tân"],
    "Văn hóa và tham quan": ["bảo tàng", "phố cổ", "chùa", "di tích", "tham quan"],
    "Chi phí": ["giá", "vé", "chi phí", "ngân sách", "rẻ", "đắt"],
}


def extract_intent_and_entities(
    text: str,
    hf_intent_scores: dict[str, float] | None = None,
    hf_entities: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Classify user intent and extract useful travel entities."""
    normalized = normalize_text(text)
    lowered = normalized.lower()

    scores = {label: 0.0 for label in INTENT_LABELS}
    for label, keywords in INTENT_KEYWORDS.items():
        scores[label] += sum(1.0 for keyword in keywords if keyword in lowered)

    if re.search(r"\b\d+\s*(?:ngày|đêm|tuần)\b", lowered) and "đi" in lowered:
        scores["itinerary_planning"] += 2.5

    if hf_intent_scores:
        for label, score in hf_intent_scores.items():
            if label in scores:
                scores[label] += float(score) * 2

    intent = max(scores, key=scores.get) if normalized else "travel_chat"
    if scores[intent] == 0:
        intent = "travel_chat"

    entities = _extract_rule_based_entities(normalized)
    for entity in hf_entities or []:
        text_value = entity.get("text")
        type_value = entity.get("type")
        if text_value and type_value:
            entities.append({"text": text_value, "type": type_value, "source": "huggingface"})

    return {
        "intent": intent,
        "confidence_hint": round(min(0.95, 0.45 + scores[intent] * 0.15), 2),
        "entities": entities,
        "scores": {label: round(value, 3) for label, value in scores.items() if value > 0},
    }


def analyze_sentiment_aspects(review: str) -> dict[str, Any]:
    """Analyze sentiment by travel aspects using transparent keyword heuristics."""
    normalized = normalize_text(review)
    lowered = normalized.lower()
    aspect_results: list[dict[str, Any]] = []
    total_score = 0

    for aspect, keywords in ASPECT_KEYWORDS.items():
        if not any(keyword in lowered for keyword in keywords):
            continue
        snippets = _sentences_with_keywords(normalized, keywords)
        context = " ".join(snippets).lower() if snippets else lowered
        positive_hits = [word for word in POSITIVE_WORDS if word in context]
        negative_hits = [word for word in NEGATIVE_WORDS if word in context]
        score = len(positive_hits) - len(negative_hits)
        total_score += score
        aspect_results.append(
            {
                "aspect": aspect,
                "sentiment": _score_to_label(score),
                "score": score,
                "evidence": snippets[:2],
                "positive_terms": positive_hits,
                "negative_terms": negative_hits,
            }
        )

    if not aspect_results:
        positive_hits = [word for word in POSITIVE_WORDS if word in lowered]
        negative_hits = [word for word in NEGATIVE_WORDS if word in lowered]
        total_score = len(positive_hits) - len(negative_hits)

    return {
        "overall_sentiment": _score_to_label(total_score),
        "overall_score": total_score,
        "aspects": aspect_results,
    }


def detect_topics(reviews: list[str]) -> dict[str, Any]:
    """Detect recurring topics from a list of travel reviews."""
    joined = " ".join(normalize_text(review).lower() for review in reviews)
    topic_counts: dict[str, int] = {}
    topic_terms: dict[str, list[str]] = {}

    for topic, keywords in TOPIC_KEYWORDS.items():
        hits = [keyword for keyword in keywords if keyword in joined]
        if hits:
            topic_counts[topic] = len(hits)
            topic_terms[topic] = hits

    tokens = re.findall(r"[\wÀ-ỹ]+", joined)
    stopwords = {
        "và",
        "là",
        "có",
        "rất",
        "mình",
        "tôi",
        "cho",
        "với",
        "này",
        "được",
        "không",
        "nhưng",
        "khi",
        "một",
        "các",
        "ở",
    }
    keywords = [
        word
        for word, count in Counter(tokens).most_common(20)
        if len(word) > 2 and word not in stopwords and count >= 1
    ][:10]

    return {
        "topics": [
            {"topic": topic, "count": count, "terms": topic_terms[topic]}
            for topic, count in sorted(topic_counts.items(), key=lambda item: item[1], reverse=True)
        ],
        "top_keywords": keywords,
        "review_count": len(reviews),
    }


def summarize_aspect_table(review: str) -> list[dict[str, Any]]:
    result = analyze_sentiment_aspects(review)
    return [
        {
            "Khía cạnh": item["aspect"],
            "Cảm xúc": item["sentiment"],
            "Điểm": item["score"],
            "Bằng chứng": " | ".join(item["evidence"]),
        }
        for item in result["aspects"]
    ]


def _extract_rule_based_entities(text: str) -> list[dict[str, str]]:
    entities: list[dict[str, str]] = []
    lowered = text.lower()

    for place in KNOWN_PLACES:
        if place.lower() in lowered:
            entities.append({"text": place, "type": "LOCATION", "source": "rules"})

    for match in re.findall(r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b", text):
        entities.append({"text": match, "type": "DATE", "source": "rules"})

    for match in re.findall(r"\b\d+\s*(?:ngày|đêm|tuần)\b", lowered):
        entities.append({"text": match, "type": "DURATION", "source": "rules"})

    for match in re.findall(r"\b\d+(?:[.,]\d+)?\s*(?:triệu|tr|k|vnd|đồng|usd)\b", lowered):
        entities.append({"text": match, "type": "BUDGET", "source": "rules"})

    return _dedupe_entities(entities)


def _sentences_with_keywords(text: str, keywords: list[str]) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [sentence.strip() for sentence in sentences if any(keyword in sentence.lower() for keyword in keywords)]


def _score_to_label(score: int) -> str:
    if score > 0:
        return "Tích cực"
    if score < 0:
        return "Tiêu cực"
    return "Trung lập"


def _dedupe_entities(entities: list[dict[str, str]]) -> list[dict[str, str]]:
    seen = set()
    result = []
    for entity in entities:
        key = (entity["text"].lower(), entity["type"])
        if key not in seen:
            seen.add(key)
            result.append(entity)
    return result
