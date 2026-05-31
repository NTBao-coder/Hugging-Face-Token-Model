"""Topic Detection and Clustering module utilizing BERTopic with fallback to Scikit-Learn (translation supported)."""

import numpy as np
import pandas as pd
from typing import Any, Tuple, List
from modules import get_inference_client, get_hf_token
from modules.translation import TranslationService
from utils.language_detect import LanguageDetector

# Predefined candidate topic names for zero-shot auto-labeling (English/Vietnamese mappings)
CANDIDATE_TOPICS_EN = [
    "Beach and Resort",
    "Local Cuisine",
    "Transportation & Location",
    "Hotel Service & Reception",
    "Room Quality & Amenities",
    "Cost & Price",
    "Culture & Sightseeing"
]

EN_TO_VI_TOPICS = {
    "Beach and Resort": "Biển và nghỉ dưỡng",
    "Local Cuisine": "Ẩm thực địa phương",
    "Transportation & Location": "Di chuyển & Vị trí",
    "Hotel Service & Reception": "Dịch vụ khách sạn & Lễ tân",
    "Room Quality & Amenities": "Chất lượng phòng & Tiện nghi",
    "Cost & Price": "Chi phí & Giá cả",
    "Culture & Sightseeing": "Văn hóa & Tham quan",
    "Chủ đề chung": "Chủ đề chung",
    "Outliers": "Ngoại lệ / Khác"
}

TOPIC_KEYWORDS = {
    "Beach and Resort": ["beach", "pool", "sun", "sea", "resort", "ocean", "biển", "hồ bơi", "nghỉ dưỡng"],
    "Local Cuisine": ["food", "breakfast", "restaurant", "menu", "delicious", "seafood", "đồ ăn", "ẩm thực", "nhà hàng"],
    "Transportation & Location": ["taxi", "car", "airport", "walk", "traffic", "near", "location", "xe", "di chuyển", "vị trí"],
    "Hotel Service & Reception": ["staff", "service", "reception", "friendly", "helpful", "nhân viên", "dịch vụ", "lễ tân"],
    "Room Quality & Amenities": ["room", "bed", "wifi", "ac", "bathroom", "shower", "phòng", "tiện nghi", "wifi"],
    "Cost & Price": ["price", "cost", "value", "expensive", "cheap", "giá", "chi phí", "đắt", "rẻ"],
    "Culture & Sightseeing": ["museum", "temple", "tour", "visit", "guide", "sightseeing", "tham quan", "văn hóa"]
}

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
        translator = TranslationService()
        
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
            label_en = self._auto_label(rep_text)
            label_vi = EN_TO_VI_TOPICS.get(label_en, label_en)
            
            # Translate representation words to Vietnamese
            rep_words_vi = [translator.translate(w, src="en", dest="vi") for w in rep_words]
            
            self.topics[i] = [(word, float(centroid[vectorizer.vocabulary_.get(word, 0)])) for word in rep_words]
            
            # Count size of cluster
            size = labels.count(i)
            topic_data.append({
                "Topic": i,
                "Count": size,
                "Name": f"{i}_{label_vi}",
                "Representation": rep_words_vi
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
                    return res["labels"][0]
                return res[0].label
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
    """Identify the primary topic of a single review using Zero-Shot classification (translation supported)."""
    lang = LanguageDetector.detect(text)
    translated_text = text
    
    if lang == "vi":
        try:
            translator = TranslationService()
            translated_text = translator.translate(text, src="vi", dest="en")
        except Exception:
            pass
            
    if not topics:
        topics = CANDIDATE_TOPICS_EN
        
    client = get_inference_client()
    if client is None:
        # Local keyword-based matcher
        lowered = text.lower()
        scores = {topic: 0 for topic in TOPIC_KEYWORDS}
        for topic, keywords in TOPIC_KEYWORDS.items():
            scores[topic] = sum(1 for kw in keywords if kw in lowered)
        best_topic = max(scores, key=scores.get)
        best_topic_vi = EN_TO_VI_TOPICS.get(best_topic, best_topic)
        if scores[best_topic] == 0:
            return {"topic": "Chủ đề chung", "score": 0.5, "source": "heuristic"}
        return {"topic": best_topic_vi, "score": 0.7, "source": "heuristic"}
        
    try:
        res = client.zero_shot_classification(
            translated_text,
            topics,
            model="facebook/bart-large-mnli"
        )
        best_topic = res["labels"][0] if isinstance(res, dict) else res[0].label
        best_topic_vi = EN_TO_VI_TOPICS.get(best_topic, best_topic)
        score = res["scores"][0] if isinstance(res, dict) else res[0].score
        return {"topic": best_topic_vi, "score": round(score, 3), "source": "huggingface"}
    except Exception:
        # Fallback to keyword matcher
        lowered = text.lower()
        scores = {topic: 0 for topic in TOPIC_KEYWORDS}
        for topic, keywords in TOPIC_KEYWORDS.items():
            scores[topic] = sum(1 for kw in keywords if kw in lowered)
        best_topic = max(scores, key=scores.get)
        best_topic_vi = EN_TO_VI_TOPICS.get(best_topic, best_topic)
        return {"topic": best_topic_vi, "score": 0.6, "source": "heuristic_fallback"}


def detect_topics_bertopic(docs: List[str]) -> Tuple[List[int], Any]:
    """
    Cluster docs and extract topics using BERTopic (with translation layer).
    """
    # 1. Detect if inputs are Vietnamese
    is_vi = any(LanguageDetector.detect(doc) == "vi" for doc in docs[:min(5, len(docs))])
    
    translated_docs = docs
    translator = TranslationService()
    if is_vi:
        try:
            translated_docs = translator.batch_translate(docs, src="vi", dest="en")
        except Exception:
            pass
            
    try:
        from bertopic import BERTopic
        from sentence_transformers import SentenceTransformer
        
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        topic_model = BERTopic(
            embedding_model=embedding_model,
            min_topic_size=min(2, len(docs)),
            nr_topics="auto"
        )
        topics, _ = topic_model.fit_transform(translated_docs)
        
        # Zero-shot label naming for topic representations
        topic_info = topic_model.get_topic_info()
        client = get_inference_client()
        
        updated_names = {}
        for index, row in topic_info.iterrows():
            topic_id = row["Topic"]
            if topic_id == -1:
                updated_names[-1] = "-1_Ngoại lệ / Khác"
                continue
                
            rep_words = [w for w, _ in topic_model.get_topic(topic_id)[:5]]
            rep_text = " ".join(rep_words)
            
            label_en = "General Topic"
            if client is not None:
                try:
                    res = client.zero_shot_classification(
                        rep_text,
                        CANDIDATE_TOPICS_EN,
                        model="facebook/bart-large-mnli"
                    )
                    label_en = res["labels"][0] if isinstance(res, dict) else res[0].label
                except Exception:
                    pass
            else:
                # Local keyword mapping
                scores = {topic: 0 for topic in TOPIC_KEYWORDS}
                for topic, keywords in TOPIC_KEYWORDS.items():
                    for word in rep_words:
                        if any(kw in word or word in kw for kw in keywords):
                            scores[topic] += 1
                best_t = max(scores, key=scores.get)
                if scores[best_t] > 0:
                    label_en = best_t
            
            label_vi = EN_TO_VI_TOPICS.get(label_en, label_en)
            updated_names[topic_id] = f"{topic_id}_{label_vi}"
            
        topic_model.set_topic_labels(updated_names)
        
        return topics, topic_model
        
    except Exception:
        # Fallback to KMeans if BERTopic is missing or fails (e.g., dataset size issues)
        model = FallbackTopicModel(n_clusters=max(2, len(docs) // 3))
        topics, fitted_model = model.fit_transform(translated_docs)
        return topics, fitted_model
