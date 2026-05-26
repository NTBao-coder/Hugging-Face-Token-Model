"""Static English-Vietnamese label mappings for MyTravelHelper results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LABEL_PATH = PROJECT_ROOT / "config" / "vi_labels.json"

DEFAULT_LABELS: dict[str, dict[str, str]] = {
    "sentiment": {
        "POSITIVE": "TÍCH CỰC",
        "NEGATIVE": "TIÊU CỰC",
        "NEUTRAL": "TRUNG LẬP",
    },
    "intent": {
        "book hotel": "đặt khách sạn",
        "find restaurant": "tìm nhà hàng",
        "get directions": "hỏi đường",
        "check weather": "hỏi thời tiết",
        "find attraction": "tìm điểm tham quan",
        "cancel booking": "hủy đặt chỗ",
        "make complaint": "phản ánh/khiếu nại",
        "request info": "hỏi thông tin",
    },
    "aspects": {
        "room": "phòng",
        "cleanliness": "vệ sinh",
        "staff": "nhân viên",
        "service": "dịch vụ",
        "location": "vị trí",
        "food": "đồ ăn",
        "price": "giá cả",
        "wifi": "wifi",
        "pool": "hồ bơi",
    },
    "entity_types": {
        "LOC": "ĐỊA ĐIỂM",
        "LOCATION": "ĐỊA ĐIỂM",
        "PER": "CON NGƯỜI",
        "PERSON": "CON NGƯỜI",
        "ORG": "TỔ CHỨC",
        "ORGANIZATION": "TỔ CHỨC",
        "DATE": "THỜI GIAN",
        "DURATION": "KHOẢNG THỜI GIAN",
        "BUDGET": "NGÂN SÁCH",
        "QUANTITY": "SỐ LƯỢNG",
        "MISC": "KHÁC",
    },
}


def load_labels() -> dict[str, dict[str, str]]:
    if not LABEL_PATH.exists():
        return DEFAULT_LABELS
    try:
        with LABEL_PATH.open("r", encoding="utf-8") as file:
            loaded = json.load(file)
    except (OSError, json.JSONDecodeError):
        return DEFAULT_LABELS

    labels = {section: values.copy() for section, values in DEFAULT_LABELS.items()}
    for section, values in loaded.items():
        if isinstance(values, dict):
            labels.setdefault(section, {}).update({str(k): str(v) for k, v in values.items()})
    return labels


LABELS = load_labels()


def map_label(section: str, value: Any, default: str | None = None) -> str:
    key = str(value)
    return LABELS.get(section, {}).get(key, default if default is not None else key)


def map_sentiment(label: str) -> str:
    return map_label("sentiment", label.upper())


def map_intent(intent: str) -> str:
    return map_label("intent", intent)


def map_aspect(aspect: str) -> str:
    return map_label("aspects", aspect)


def map_entity_type(entity_type: str) -> str:
    return map_label("entity_types", entity_type.upper())

