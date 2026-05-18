"""Streamlit app for MyTravelHelper."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.inference import HuggingFaceService
from modules.nlp_tasks import (
    INTENT_LABELS,
    analyze_sentiment_aspects,
    detect_topics,
    extract_intent_and_entities,
    summarize_aspect_table,
)
from modules.utils import pipeline_mermaid, split_reviews


st.set_page_config(page_title="MyTravelHelper", layout="wide")


@st.cache_resource
def get_hf_service() -> HuggingFaceService:
    return HuggingFaceService()


hf_service = get_hf_service()
status = hf_service.healthcheck()

st.title("MyTravelHelper")
st.caption("Ứng dụng trợ lý du lịch dùng Streamlit và Hugging Face Inference Providers")

with st.sidebar:
    st.header("Trạng thái")
    if status["ok"]:
        st.success(status["message"])
    else:
        st.warning(status["message"])

    st.subheader("Model dự kiến")
    st.code(
        "\n".join(
            [
                hf_service.config.chat_model,
                hf_service.config.zero_shot_model,
                hf_service.config.ner_model,
                hf_service.config.sentiment_model,
            ]
        ),
        language="text",
    )

tab_chat, tab_review, tab_intent, tab_topics, tab_pipeline = st.tabs(
    ["Chatbot du lịch", "Phân tích review", "Intent & NER", "Topic", "Pipeline"]
)

with tab_chat:
    st.subheader("Chatbot du lịch")
    question = st.text_area(
        "Yêu cầu của người dùng",
        value="Gợi ý lịch trình 2 ngày ở Đà Nẵng cho ngân sách 3 triệu.",
        height=120,
    )
    if st.button("Tư vấn", type="primary"):
        with st.spinner("Đang xử lý..."):
            intent_result = extract_intent_and_entities(
                question,
                hf_service.zero_shot_intent(question, INTENT_LABELS),
                hf_service.named_entities(question),
            )
            answer = hf_service.travel_chat(question)
        st.markdown("#### Phản hồi")
        st.write(answer)
        st.markdown("#### Intent filtering")
        st.json(intent_result)

with tab_review:
    st.subheader("Phân tích cảm xúc theo khía cạnh")
    review = st.text_area(
        "Review du lịch",
        value=(
            "Khách sạn có vị trí gần biển, phòng sạch và view đẹp. "
            "Nhân viên thân thiện nhưng bữa sáng hơi ít món. Giá khá đáng tiền."
        ),
        height=140,
    )
    if st.button("Phân tích cảm xúc", type="primary"):
        result = analyze_sentiment_aspects(review)
        st.metric("Cảm xúc tổng quan", result["overall_sentiment"], result["overall_score"])
        table = summarize_aspect_table(review)
        if table:
            st.dataframe(pd.DataFrame(table), use_container_width=True, hide_index=True)
        else:
            st.info("Chưa nhận diện được khía cạnh cụ thể trong review này.")

with tab_intent:
    st.subheader("Phân loại ý định và trích xuất thực thể")
    intent_text = st.text_input(
        "Câu hỏi",
        value="Mình muốn đi Hội An 3 ngày với ngân sách 4 triệu, nên tham quan ở đâu?",
    )
    if st.button("Nhận diện intent / entities", type="primary"):
        result = extract_intent_and_entities(
            intent_text,
            hf_service.zero_shot_intent(intent_text, INTENT_LABELS),
            hf_service.named_entities(intent_text),
        )
        st.json(result)

with tab_topics:
    st.subheader("Phát hiện chủ đề trong nhiều review")
    raw_reviews = st.text_area(
        "Mỗi dòng là một review",
        value=(
            "Biển đẹp, hải sản ngon, giá hơi cao.\n"
            "Khách sạn gần trung tâm, phòng sạch, lễ tân hỗ trợ nhanh.\n"
            "Di chuyển từ sân bay tiện, nhưng vé tham quan khá đắt."
        ),
        height=170,
    )
    if st.button("Phát hiện topic", type="primary"):
        reviews = split_reviews(raw_reviews)
        result = detect_topics(reviews)
        if result["topics"]:
            df = pd.DataFrame(result["topics"])
            st.dataframe(df, use_container_width=True, hide_index=True)
            chart_df = df[["topic", "count"]]
            st.bar_chart(chart_df.set_index("topic"))
        st.markdown("#### Từ khóa nổi bật")
        st.write(", ".join(result["top_keywords"]) or "Chưa có dữ liệu.")

with tab_pipeline:
    st.subheader("Kiến trúc tổng quát")
    st.markdown("```mermaid\n" + pipeline_mermaid().strip() + "\n```")
    st.markdown(
        """
1. Streamlit nhận câu hỏi hoặc review.
2. Module NLP phân loại ý định và trích xuất thực thể.
3. Router chọn chức năng phù hợp: chat, sentiment, topic.
4. Hugging Face Inference Providers được dùng khi có `HF_TOKEN`; fallback cục bộ giúp demo vẫn chạy.
5. Kết quả được trình bày lại bằng bảng, biểu đồ hoặc JSON để kiểm thử.
"""
    )
