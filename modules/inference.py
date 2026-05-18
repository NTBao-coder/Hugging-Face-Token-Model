"""Hugging Face Inference Providers integration layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from modules.utils import get_hf_token, normalize_text


@dataclass(frozen=True)
class ModelConfig:
    chat_model: str = "mistralai/Mistral-7B-Instruct-v0.2"
    zero_shot_model: str = "facebook/bart-large-mnli"
    ner_model: str = "dslim/bert-base-NER"
    sentiment_model: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"


class HuggingFaceService:
    """Small wrapper around huggingface_hub with graceful local fallbacks."""

    def __init__(self, config: ModelConfig | None = None) -> None:
        self.config = config or ModelConfig()
        self.token = get_hf_token()
        self._client: Any | None = None
        self.last_error: str | None = None

    @property
    def configured(self) -> bool:
        return bool(self.token)

    @property
    def client(self) -> Any:
        if self._client is None:
            from huggingface_hub import InferenceClient

            self._client = InferenceClient(token=self.token)
        return self._client

    def healthcheck(self) -> dict[str, str | bool]:
        if not self.configured:
            return {
                "ok": False,
                "mode": "offline",
                "message": "Chưa có HF_TOKEN. App sẽ chạy bằng fallback cục bộ.",
            }
        return {
            "ok": True,
            "mode": "huggingface",
            "message": "Đã tìm thấy HF_TOKEN. Sẵn sàng gọi Hugging Face Inference Providers.",
        }

    def travel_chat(self, user_message: str) -> str:
        """Generate a travel-assistant response with a conservative fallback."""
        message = normalize_text(user_message)
        if not message:
            return "Bạn hãy nhập câu hỏi du lịch cụ thể hơn nhé."

        fallback = (
            "Gợi ý nhanh: hãy xác định điểm đến, thời gian, ngân sách và phong cách du lịch. "
            f"Với yêu cầu '{message}', bạn có thể bắt đầu bằng lịch trình 1-2 ngày, "
            "ưu tiên địa điểm gần nhau, thêm phương án ăn uống và phương án dự phòng khi thời tiết xấu."
        )
        if not self.configured:
            return fallback

        prompt = (
            "Bạn là MyTravelHelper, trợ lý du lịch nói tiếng Việt. "
            "Trả lời ngắn gọn, thực tế, có cấu trúc.\n\n"
            f"Người dùng: {message}\nTrợ lý:"
        )
        try:
            return self.client.text_generation(
                prompt,
                model=self.config.chat_model,
                max_new_tokens=256,
                temperature=0.4,
                return_full_text=False,
            ).strip()
        except Exception as exc:  # noqa: BLE001 - show a friendly fallback in UI.
            self.last_error = str(exc)
            return fallback

    def zero_shot_intent(self, text: str, labels: list[str]) -> dict[str, float]:
        """Try zero-shot classification and return label scores."""
        if not self.configured:
            return {}
        try:
            result = self.client.zero_shot_classification(
                normalize_text(text),
                labels,
                model=self.config.zero_shot_model,
            )
            if isinstance(result, dict):
                return dict(zip(result.get("labels", []), result.get("scores", []), strict=False))
            return {item.label: float(item.score) for item in result}
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            return {}

    def named_entities(self, text: str) -> list[dict[str, Any]]:
        """Run token classification for NER when Hugging Face is configured."""
        if not self.configured:
            return []
        try:
            entities = self.client.token_classification(
                normalize_text(text),
                model=self.config.ner_model,
                aggregation_strategy="simple",
            )
            normalized = []
            for entity in entities:
                normalized.append(
                    {
                        "text": getattr(entity, "word", None) or entity.get("word"),
                        "type": getattr(entity, "entity_group", None) or entity.get("entity_group"),
                        "score": float(getattr(entity, "score", None) or entity.get("score", 0)),
                    }
                )
            return normalized
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            return []

    def sentiment(self, text: str) -> list[dict[str, float | str]]:
        """Call a sentiment model when available."""
        if not self.configured:
            return []
        try:
            result = self.client.text_classification(
                normalize_text(text),
                model=self.config.sentiment_model,
            )
            return [
                {
                    "label": getattr(item, "label", None) or item.get("label"),
                    "score": float(getattr(item, "score", None) or item.get("score", 0)),
                }
                for item in result
            ]
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            return []
