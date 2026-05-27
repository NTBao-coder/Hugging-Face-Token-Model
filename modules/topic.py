"""Topic Detection and Clustering module utilizing BERTopic with fallback to Scikit-Learn."""

import numpy as np
import pandas as pd
from typing import Any, Tuple, List
from modules import get_inference_client, get_hf_token
from modules.translation import TranslationService, TranslationError
from utils.language_detect import LanguageDetector
from utils.preprocessing import normalize_vietnamese_text

# Predefined candidate topic names for zero-shot auto-labeling
CANDIDATE_TOPICS = [
    "Biển và nghỉ dưỡng",
    "Ẩm thực địa phương",
    "Di chuyển & Vị trí",
    "Dịch vụ khách sạn & Lễ tân",
    "Chất lượng phòng & Tiện nghi",
    "Chi phí & Giá cả",
    "Văn hóa & Tham quan"
]

CANDIDATE_TOPICS_EN_TO_VI = {
    "Beach and resort": "Biển và nghỉ dưỡng",
    "Local food": "Ẩm thực địa phương",
    "Transportation and location": "Di chuyển & Vị trí",
    "Hotel service and reception": "Dịch vụ khách sạn & Lễ tân",
    "Room quality and amenities": "Chất lượng phòng & Tiện nghi",
    "Costs and prices": "Chi phí & Giá cả",
    "Culture and sightseeing": "Văn hóa & Tham quan",
}

CANDIDATE_TOPICS_EN = list(CANDIDATE_TOPICS_EN_TO_VI.keys())

TOPIC_KEYWORDS = {
    "Biển và nghỉ dưỡng": ["biển", "resort", "hồ bơi", "view", "nắng", "đảo", "beach", "pool", "sun"],
    "Ẩm thực địa phương": ["đồ ăn", "món", "nhà hàng", "chợ", "hải sản", "bữa sáng", "food", "breakfast", "restaurant"],
    "Di chuyển & Vị trí": ["taxi", "xe", "sân bay", "đi bộ", "di chuyển", "kẹt xe", "gần", "location", "near", "airport"],
    "Dịch vụ khách sạn & Lễ tân": ["nhân viên", "phục vụ", "lễ tân", "hỗ trợ", "staff", "service", "reception"],
    "Chất lượng phòng & Tiện nghi": ["phòng", "homestay", "giường", "wifi", "điều hòa", "room", "bed", "wifi", "ac"],
    "Chi phí & Giá cả": ["giá", "vé", "chi phí", "ngân sách", "rẻ", "đắt", "price", "cost", "value"],
    "Văn hóa & Tham quan": ["bảo tàng", "phố cổ", "chùa", "di tích", "tham quan", "visit", "tourist", "sightseeing"]
}


def _prepare_topic_docs(docs: List[str]) -> dict[str, Any]:
    """Normalize and translate Vietnamese review batches before topic modeling."""
    normalized_docs = [normalize_vietnamese_text(doc) for doc in docs if doc and doc.strip()]
    translator = TranslationService()
    detector = LanguageDetector(translator)
    detections = [detector.detect(doc) for doc in normalized_docs]
    has_vietnamese = any(item.language == "vi" for item in detections)

    if not has_vietnamese:
        return {
            "docs_for_model": normalized_docs,
            "translated_docs": [],
            "detected_languages": [item.language for item in detections],
            "translation_source": "bypass",
        }

    translated_docs = []
    for doc, detection in zip(normalized_docs, detections):
        if detection.language != "vi":
            translated_docs.append(doc)
            continue
        try:
            translated_docs.append(translator.translate(doc, src="vi", dest="en"))
        except TranslationError:
            translated_docs.append(doc)

    return {
        "docs_for_model": translated_docs,
        "translated_docs": translated_docs,
        "detected_languages": [item.language for item in detections],
        "translation_source": translator.backend,
    }


def _topic_label_to_vi(label: str) -> str:
    return CANDIDATE_TOPICS_EN_TO_VI.get(label, label)

class FallbackTopicModel:
    """A Scikit-Learn KMeans + TF-IDF fallback that mimics BERTopic's API."""
    def __init__(self, n_clusters: int = 3):
        self.n_clusters = n_clusters
        self.topic_info_df = None
        self.topics = {}
        self.docs_assigned = []

    def fit_transform(self, docs: List[str]) -> Tuple[List[int], Any]:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.cluster import KMeans

        n_samples = len(docs)
        k = min(self.n_clusters, n_samples)
        if k < 1:
            k = 1

        # Extract features
        vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
        X = vectorizer.fit_transform(docs)
        
        # Fit KMeans
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        labels = list(kmeans.fit(X).labels_)
        self.docs_assigned = labels

        # Identify representative words for each cluster
        terms = vectorizer.get_feature_names_out()
        centroids = kmeans.cluster_centers_
        
        topic_data = []
        for i in range(k):
            # Get top 5 terms in cluster
            centroid = centroids[i]
            top_term_indices = centroid.argsort()[-5:][::-1]
            rep_words = [terms[idx] for idx in top_term_indices if centroid[idx] > 0]
            
            # If no terms have weight, use placeholders
            if not rep_words:
                rep_words = ["travel", "hotel", "service"]
                
            # Assign label using zero-shot classification or keywords
            rep_text = " ".join(rep_words)
            label = self._auto_label(rep_text)
            
            self.topics[i] = [(word, float(centroid[vectorizer.vocabulary_.get(word, 0)])) for word in rep_words]
            
            # Count size of cluster
            size = labels.count(i)
            topic_data.append({
                "Topic": i,
                "Count": size,
                "Name": f"{i}_{label}",
                "Representation": rep_words
            })
            
        self.topic_info_df = pd.DataFrame(topic_data)
        return labels, self

    def _auto_label(self, rep_text: str) -> str:
        """Classify representative words using zero-shot or keyword matching."""
        client = get_inference_client()
        if client is not None:
            try:
                res = client.zero_shot_classification(
                    rep_text,
                    CANDIDATE_TOPICS_EN,
                    model="facebook/bart-large-mnli"
                )
                if isinstance(res, dict):
                    return _topic_label_to_vi(res["labels"][0])
                return _topic_label_to_vi(res[0].label)
            except Exception:
                pass
                
        # Heuristic mapping fallback
        scores = {topic: 0 for topic in TOPIC_KEYWORDS}
        rep_words_list = rep_text.lower().split()
        for topic, keywords in TOPIC_KEYWORDS.items():
            for word in rep_words_list:
                if any(kw in word or word in kw for kw in keywords):
                    scores[topic] += 1
        best_topic = max(scores, key=scores.get)
        if scores[best_topic] == 0:
            return "Chủ đề chung"
        return best_topic

    def get_topic_info(self) -> pd.DataFrame:
        return self.topic_info_df

    def get_topic(self, topic_id: int) -> List[Tuple[str, float]]:
        return self.topics.get(topic_id, [])


def detect_topics_zeroshot(text: str, topics: List[str] | None = None) -> dict[str, Any]:
    """Identify the primary topic of a single review using Zero-Shot classification."""
    prepared = _prepare_topic_docs([text])
    text_for_model = prepared["docs_for_model"][0] if prepared["docs_for_model"] else text
    candidate_labels = topics or CANDIDATE_TOPICS_EN
        
    client = get_inference_client()
    if client is None:
        # Local keyword-based matcher
        lowered = text.lower()
        scores = {topic: 0 for topic in TOPIC_KEYWORDS}
        for topic, keywords in TOPIC_KEYWORDS.items():
            scores[topic] = sum(1 for kw in keywords if kw in lowered)
        best_topic = max(scores, key=scores.get)
        if scores[best_topic] == 0:
            return {"topic": "Chủ đề chung", "score": 0.5, "source": "heuristic", **prepared}
        return {"topic": best_topic, "score": 0.7, "source": "heuristic", **prepared}
        
    try:
        res = client.zero_shot_classification(
            text_for_model,
            candidate_labels,
            model="facebook/bart-large-mnli"
        )
        if isinstance(res, dict):
            label = res["labels"][0]
            score = res["scores"][0]
        else:
            label = res[0].label
            score = res[0].score
        return {
            "topic": _topic_label_to_vi(label),
            "topic_en": label,
            "score": round(score, 3),
            "source": "huggingface",
            **prepared,
        }
    except Exception:
        # Fallback to keyword matcher
        lowered = text.lower()
        scores = {topic: 0 for topic in TOPIC_KEYWORDS}
        for topic, keywords in TOPIC_KEYWORDS.items():
            scores[topic] = sum(1 for kw in keywords if kw in lowered)
        best_topic = max(scores, key=scores.get)
        return {"topic": best_topic, "score": 0.6, "source": "heuristic_fallback", **prepared}


def detect_topics_bertopic(docs: List[str]) -> Tuple[List[int], Any]:
    """
    Cluster docs and extract topics using BERTopic.
    
    If BERTopic is not installed or import fails, falls back gracefully to FallbackTopicModel.
    """
    prepared = _prepare_topic_docs(docs)
    docs_for_model = prepared["docs_for_model"]

    try:
        from bertopic import BERTopic
        from sentence_transformers import SentenceTransformer
        
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        topic_model = BERTopic(
            embedding_model=embedding_model,
            min_topic_size=min(2, len(docs)),
            nr_topics="auto"
        )
        topics, _ = topic_model.fit_transform(docs_for_model)
        topic_model.source_docs = docs
        topic_model.translated_docs = prepared["translated_docs"]
        topic_model.detected_languages = prepared["detected_languages"]
        
        # Zero-shot label naming for topic representations
        topic_info = topic_model.get_topic_info()
        client = get_inference_client()
        
        if client is not None:
            updated_names = {}
            for index, row in topic_info.iterrows():
                topic_id = row["Topic"]
                if topic_id == -1:
                    updated_names[-1] = "-1_Outliers"
                    continue
                rep_words = [w for w, _ in topic_model.get_topic(topic_id)[:5]]
                rep_text = " ".join(rep_words)
                try:
                    res = client.zero_shot_classification(
                        rep_text,
                        CANDIDATE_TOPICS_EN,
                        model="facebook/bart-large-mnli"
                    )
                    label = res["labels"][0] if isinstance(res, dict) else res[0].label
                    updated_names[topic_id] = f"{topic_id}_{_topic_label_to_vi(label)}"
                except Exception:
                    updated_names[topic_id] = f"{topic_id}_Topic {topic_id}"
            
            # Map names
            topic_model.set_topic_labels(updated_names)
            
        return topics, topic_model
        
    except ImportError:
        # Fallback to KMeans
        model = FallbackTopicModel(n_clusters=max(2, len(docs_for_model) // 3))
        topics, fitted_model = model.fit_transform(docs_for_model)
        fitted_model.source_docs = docs
        fitted_model.translated_docs = prepared["translated_docs"]
        fitted_model.detected_languages = prepared["detected_languages"]
        return topics, fitted_model
