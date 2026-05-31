import os
import json
import logging

class LabelMapper:
    """Utility to map English labels/aspects to Vietnamese translations."""
    def __init__(self):
        self.mapping = {}
        self._load_config()

    def _load_config(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(os.path.dirname(current_dir), "config", "vi_labels.json")
        
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    self.mapping = json.load(f)
            else:
                logging.warning(f"Config path {config_path} does not exist. Using fallbacks.")
        except Exception as e:
            logging.error(f"Error loading vi_labels.json: {e}")

        # Inline fallback defaults
        if not self.mapping:
            self.mapping = {
                "sentiment": {
                    "POSITIVE": "TÍCH CỰC",
                    "NEGATIVE": "TIÊU CỰC",
                    "NEUTRAL": "TRUNG LẬP"
                },
                "intent": {
                    "book hotel": "đặt khách sạn",
                    "find restaurant": "tìm nhà hàng",
                    "get directions": "hỏi đường / chỉ đường",
                    "check weather": "hỏi thời tiết",
                    "find attraction": "tìm điểm tham quan",
                    "cancel booking": "hủy đặt chỗ",
                    "make complaint": "phản ánh / khiếu nại",
                    "request info": "hỏi thông tin chung"
                },
                "aspects": {
                    "room": "phòng ốc",
                    "cleanliness": "vệ sinh",
                    "staff": "nhân viên",
                    "service": "dịch vụ",
                    "location": "vị trí",
                    "food": "đồ ăn",
                    "price": "giá cả",
                    "wifi": "wifi",
                    "pool": "hồ bơi"
                },
                "entity_types": {
                    "LOCATION": "ĐỊA ĐIỂM",
                    "LOC": "ĐỊA ĐIỂM",
                    "PERSON": "CON NGƯỜI",
                    "PER": "CON NGƯỜI",
                    "ORGANIZATION": "TỔ CHỨC",
                    "ORG": "TỔ CHỨC",
                    "DATE": "THỜI GIAN",
                    "DURATION": "KHOẢNG THỜI GIAN",
                    "BUDGET": "NGÂN SÁCH",
                    "MISC": "KHÁC"
                }
            }

    def map_sentiment(self, label: str) -> str:
        """Map positive/negative/neutral to Vietnamese."""
        if not label:
            return "TRUNG LẬP"
        upper_label = label.upper()
        return self.mapping.get("sentiment", {}).get(upper_label, upper_label)

    def map_intent(self, label: str) -> str:
        """Map English intent labels to Vietnamese descriptions."""
        if not label:
            return "hỏi thông tin chung"
        lower_label = label.lower()
        return self.mapping.get("intent", {}).get(lower_label, label)

    def map_aspect(self, label: str) -> str:
        """Map aspect names (e.g. cleanliness -> vệ sinh)."""
        if not label:
            return label
        lower_label = label.lower()
        return self.mapping.get("aspects", {}).get(lower_label, label)

    def map_entity_type(self, label: str) -> str:
        """Map entity group labels to Vietnamese descriptions."""
        if not label:
            return "KHÁC"
        upper_label = label.upper()
        return self.mapping.get("entity_types", {}).get(upper_label, upper_label)
