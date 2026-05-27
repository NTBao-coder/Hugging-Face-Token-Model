"""Streamlit application for MyTravelHelper - AI-powered travel assistant."""

import os
import json
import pandas as pd
import streamlit as st

# Import utilities
from utils.preprocessing import normalize_text, split_reviews
from utils.display import (
    inject_premium_styles,
    render_main_title,
    show_aspect_sentiment_grid,
    render_entity_badges,
    show_topic_bar_chart
)

# Import modules
from modules import get_hf_token, get_inference_client
from modules.sentiment import analyze_sentiment
from modules.intent_ner import classify_intent, extract_entities, travel_chat, TRAVEL_INTENTS
from modules.topic import detect_topics_bertopic, CANDIDATE_TOPICS
from modules.translation import TranslationError, TranslationService

# Set page configuration
st.set_page_config(
    page_title="MyTravelHelper — AI Assistant",
    page_icon="🌏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load styling
inject_premium_styles()

# Healthcheck helper
def get_api_status() -> dict:
    token = get_hf_token()
    if not token:
        return {
            "ok": False,
            "mode": "Offline Heuristics",
            "message": "Không tìm thấy HF_TOKEN trong file .env. Hệ thống đang chạy ở chế độ Heuristic Fallback cục bộ."
        }
    return {
        "ok": True,
        "mode": "Hugging Face Serverless",
        "message": "Đã cấu hình HF_TOKEN thành công. Sẵn sàng kết nối tới Hugging Face Inference API."
    }

api_status = get_api_status()

# Sidebar Setup
with st.sidebar:
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 20px;'>
            <h2 style='color:#FF4B4B; font-size: 2.2rem; margin: 0;'>🌏</h2>
            <h3 style='margin: 5px 0 0 0;'>MyTravelHelper</h3>
            <p style='color:#8A90A6; font-size:0.85rem;'>Phiên bản 2.0.0 Multilingual</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.header("Cấu hình & Trạng thái")
    
    # API Status
    if api_status["ok"]:
        st.success(f"**Chế độ:** {api_status['mode']}\n\n{api_status['message']}")
    else:
        st.warning(f"**Chế độ:** {api_status['mode']}\n\n{api_status['message']}")
        
    st.divider()
    
    st.subheader("Mô hình sử dụng")
    st.markdown(
        """
        - **Chat/NLU:** `Mistral-7B-Instruct-v0.2`
        - **Intent classification:** `BART-large-mnli` (Zero-shot)
        - **Named Entity Recognition (NER):** `BERT-base-NER` + Heuristics
        - **Aspect Sentiment:** `DeBERTa-v3-base-absa-v1.1`
        - **Topic Clustering:** `BERTopic` / `KMeans` + `BART-large-mnli`
        - **Translation:** `googletrans` demo / Google Cloud Translate production
        """
    )

# Render Main Title
render_main_title()

# Define Tabs
tab_chat, tab_review, tab_topic, tab_translate, tab_pipeline = st.tabs([
    "💬 Trợ Lý Tư Vấn & NLU",
    "📊 Phân Tích Cảm Xúc Khía Cạnh",
    "🏷️ Gom Cụm Chủ Đề Review",
    "🌐 Dịch thuật EN ↔ VI",
    "⚙️ Kiến Trúc Hệ Thống"
])

# ----------------- TAB 1: CHATBOT & NLU -----------------
with tab_chat:
    st.markdown("### 💬 Trợ Lý Tư Vấn Du Lịch thông minh")
    st.markdown("Nhập câu hỏi hoặc yêu cầu du lịch của bạn bên dưới. Hệ thống sẽ phân tích ý định (Intent), trích xuất các thực thể quan trọng (Entities) và sinh câu trả lời tư vấn.")
    
    user_query = st.text_area(
        "Câu hỏi của bạn:",
        value="Mình muốn đi Đà Nẵng 3 ngày với ngân sách khoảng 5 triệu đồng khởi hành vào thứ 6 tuần tới, nên tham quan ở đâu?",
        height=100
    )
    
    if st.button("Gửi yêu cầu", type="primary", key="btn_chat"):
        if not user_query.strip():
            st.error("Vui lòng nhập câu hỏi của bạn.")
        else:
            with st.spinner("MyTravelHelper đang suy nghĩ và phân tích..."):
                # 1. Classify Intent
                intent_res = classify_intent(user_query)
                intent_en = intent_res["intent"]
                intent_vi = intent_res.get("intent_vi") or TRAVEL_INTENTS.get(intent_en, intent_en)
                
                # 2. Extract Entities
                entities = extract_entities(user_query)
                
                # 3. Generate Answer
                answer = travel_chat(user_query)
                
            # Display results in beautiful sections
            st.markdown("#### 🤖 Trợ lý phản hồi:")
            st.markdown(
                f"<div class='glass-card' style='background-color: rgba(255, 75, 75, 0.03); border-left: 4px solid #FF4B4B;'>"
                f"{answer}"
                f"</div>",
                unsafe_allow_html=True
            )
            
            st.markdown("#### 🔍 Kết quả phân tích Ngôn ngữ tự nhiên (NLU):")
            if intent_res.get("translated_text"):
                st.info(
                    f"Ngôn ngữ phát hiện: `{intent_res.get('detected_language')}` · "
                    f"Bản dịch EN dùng cho model: {intent_res['translated_text']}"
                )
            col_intent, col_entities = st.columns([1, 2])
            
            with col_intent:
                st.markdown(
                    f"""
                    <div class='glass-card'>
                        <h5 style='margin-top:0;'>Ý định người dùng (Intent)</h5>
                        <p style='font-size:1.15rem; font-weight:700; color:#4B6BFF; margin-bottom:5px;'>{intent_vi}</p>
                        <p style='font-size:0.85rem; color:#8A90A6; margin:0;'>
                            Label gốc: <code>{intent_en}</code><br>
                            Độ tin cậy: <strong>{intent_res.get('confidence', 0.0):.2f}</strong> ({intent_res.get('source', '')})
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            with col_entities:
                st.markdown(
                    """
                    <div class='glass-card' style='height: 100%;'>
                        <h5 style='margin-top:0;'>Thực thể trích xuất (Entities)</h5>
                    """,
                    unsafe_allow_html=True
                )
                render_entity_badges(entities)
                st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TAB 2: SENTIMENT & ABSA -----------------
with tab_review:
    st.markdown("### 📊 Phân tích cảm xúc theo khía cạnh (ABSA)")
    st.markdown("Nhập một đoạn review du lịch hoặc chọn một câu review mẫu để phân tích cảm xúc chung và cảm xúc đối với từng khía cạnh cụ thể (phòng, vị trí, giá cả, đồ ăn, v.v.).")
    
    sample_reviews = [
        "Khách sạn rất sạch sẽ, vị trí ngay cạnh biển Mỹ Khê rất đẹp, nhưng nhân viên phục vụ phòng còn hơi chậm.",
        "Phòng tắm khá rộng rãi nhưng wifi yếu kinh khủng, không thể làm việc được. Giá phòng lại cực kỳ đắt đỏ.",
        "Bữa sáng buffet ở đây vô cùng phong phú và hợp khẩu vị. Nhân viên lễ tân rất thân thiện và nhiệt tình hỗ trợ check-in sớm.",
        "Custom"
    ]
    
    selected_sample = st.selectbox("Chọn review mẫu:", sample_reviews, index=0)
    
    if selected_sample == "Custom":
        review_input = st.text_area("Nhập review của bạn:", value="", height=100)
    else:
        review_input = st.text_area("Nội dung review:", value=selected_sample, height=100)
        
    if st.button("Phân tích cảm xúc", type="primary", key="btn_sentiment"):
        if not review_input.strip():
            st.error("Vui lòng nhập nội dung review.")
        else:
            with st.spinner("Hệ thống đang chạy phân tích cảm xúc..."):
                # Overall sentiment
                overall = analyze_sentiment(review_input, mode="basic")
                # Aspect sentiment
                aspects = analyze_sentiment(review_input, mode="absa")
                
            st.markdown("#### Kết quả phân tích:")
            
            # Display overall metric
            color_map = {"POSITIVE": "#2ecc71", "NEGATIVE": "#e74c3c", "NEUTRAL": "#95a5a6"}
            sentiment_vi = {"POSITIVE": "Tích cực", "NEGATIVE": "Tiêu cực", "NEUTRAL": "Trung lập"}
            
            lbl = overall.get("label", "NEUTRAL")
            clr = color_map.get(lbl, "#95a5a6")
            lbl_vi = overall.get("label_vi") or sentiment_vi.get(lbl, lbl)

            if overall.get("translated_text"):
                st.info(
                    f"Ngôn ngữ phát hiện: `{overall.get('detected_language')}` · "
                    f"Bản dịch EN dùng cho model: {overall['translated_text']}"
                )
            
            st.markdown(
                f"""
                <div style='background:rgba(255,255,255,0.03); border-radius:12px; padding:20px; border:1px solid rgba(255,255,255,0.05); margin-bottom:20px; display:inline-block;'>
                    <div style='font-size:0.9rem; color:#8A90A6;'>Cảm xúc tổng thể</div>
                    <div style='font-size:2rem; font-weight:800; color:{clr};'>{lbl_vi}</div>
                    <div style='font-size:0.85rem; color:#8A90A6; margin-top:5px;'>
                        Độ tin cậy: <strong>{overall.get('score', 0.0):.2f}</strong> ({overall.get('source', '')})
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("#### Cảm xúc chi tiết theo từng khía cạnh:")
            show_aspect_sentiment_grid(aspects)

# ----------------- TAB 3: TOPIC MODELING -----------------
with tab_topic:
    st.markdown("### 🏷️ Gom cụm chủ đề từ nhiều review (Topic Detection)")
    st.markdown("Tải lên danh sách các đánh giá của du khách để tự động gom nhóm chúng vào các chủ đề chính. Hệ thống sử dụng BERTopic (hoặc mô hình Clustering dự phòng) để rút trích các từ khóa đại diện.")
    
    # Option to load sample dataset or input text
    data_option = st.radio("Nguồn dữ liệu review:", ["Dùng 20+ review mẫu từ hệ thống", "Nhập danh sách review thủ công"], horizontal=True)
    
    reviews_to_run = []
    
    if data_option == "Dùng 20+ review mẫu từ hệ thống":
        # Load sample_reviews.json
        sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_reviews.json")
        if os.path.exists(sample_path):
            with open(sample_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                reviews_to_run = [r["text"] for r in data]
            st.info(f"Đã load {len(reviews_to_run)} review mẫu từ file `data/sample_reviews.json`.")
            with st.expander("Xem trước danh sách review mẫu"):
                st.write(reviews_to_run)
        else:
            st.error("Không tìm thấy file `data/sample_reviews.json`.")
    else:
        raw_input = st.text_area(
            "Nhập danh sách review (Mỗi dòng là một review):",
            value=(
                "Bãi biển rất sạch và có bờ cát trắng cực kì thích.\n"
                "Giá phòng đắt đỏ nhưng dịch vụ thì chắp vá không tương xứng.\n"
                "Buffet ăn sáng có rất nhiều món hải sản tươi ngon đậm vị miền trung.\n"
                "Nhân viên lễ tân ăn nói trống không và thái độ thờ ơ.\n"
                "Khách sạn cách sân bay rất gần thuận tiện di chuyển nhanh chóng."
            ),
            height=150
        )
        reviews_to_run = split_reviews(raw_input)
        st.info(f"Nhận diện được {len(reviews_to_run)} review hợp lệ.")
        
    if st.button("Chạy gom cụm chủ đề", type="primary", key="btn_topic"):
        if len(reviews_to_run) < 3:
            st.error("Cần ít nhất 3 review để chạy thuật toán gom cụm chủ đề.")
        else:
            with st.spinner("Đang chạy embedding và mô hình gom cụm... (Vui lòng đợi vài giây)"):
                topics, model = detect_topics_bertopic(reviews_to_run)
                
            st.markdown("#### Kết quả gom cụm:")
            
            # Fetch topic info
            try:
                topic_info = model.get_topic_info()
            except Exception as e:
                st.error(f"Lỗi khi đọc thông tin chủ đề: {e}")
                topic_info = pd.DataFrame()
                
            if not topic_info.empty:
                col_table, col_chart = st.columns([1, 1])
                
                with col_table:
                    st.markdown("##### Bảng thống kê chủ đề")
                    # Clean presentation of topic table
                    display_df = topic_info.copy()
                    # format representation list as a string
                    if "Representation" in display_df.columns:
                        display_df["Representation"] = display_df["Representation"].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                    
                with col_chart:
                    st.markdown("##### Biểu đồ phân bố chủ đề")
                    # Prepare dataframe for chart
                    chart_df = topic_info[topic_info["Topic"] != -1].copy() # Filter outliers
                    if chart_df.empty:
                        chart_df = topic_info.copy()
                    chart_df = chart_df.rename(columns={"Name": "topic"})
                    show_topic_bar_chart(chart_df)
                    
                # Interactive inspector per topic
                st.markdown("##### Rút trích từ khóa đại diện chi tiết:")
                topic_list = topic_info["Topic"].tolist()
                selected_topic_id = st.selectbox("Chọn Chủ đề (Topic ID) để xem từ khóa chi tiết:", topic_list)
                
                rep_words = model.get_topic(selected_topic_id)
                if rep_words:
                    words_df = pd.DataFrame(rep_words, columns=["Từ khóa", "Trọng số TF-IDF"])
                    st.dataframe(words_df, use_container_width=True, hide_index=True)
                else:
                    st.info("Chủ đề này không có từ khóa đại diện riêng lẻ.")

                translated_docs = getattr(model, "translated_docs", [])
                if translated_docs:
                    with st.expander("Xem bản dịch EN đã dùng cho Topic Model"):
                        st.dataframe(
                            pd.DataFrame({
                                "Review gốc": reviews_to_run,
                                "Bản dịch EN": translated_docs,
                            }),
                            use_container_width=True,
                            hide_index=True,
                        )
            else:
                st.warning("Không phát hiện được chủ đề nào rõ rệt từ tập review.")

# ----------------- TAB 4: TRANSLATION TOOL -----------------
with tab_translate:
    st.markdown("### 🌐 Công cụ dịch thuật English ↔ Vietnamese")
    st.markdown("Dịch nhanh hai chiều để kiểm tra lớp Translate-then-Process trước khi chạy NLP model.")

    lang_options = {
        "Tiếng Việt": "vi",
        "Tiếng Anh": "en",
    }

    if "src_lang" not in st.session_state:
        st.session_state["src_lang"] = "Tiếng Việt"
    if "tgt_lang" not in st.session_state:
        st.session_state["tgt_lang"] = "Tiếng Anh"
    if "src_text" not in st.session_state:
        st.session_state["src_text"] = "Phòng rất sạch nhưng nhân viên hơi chậm."
    if "translated_text" not in st.session_state:
        st.session_state["translated_text"] = ""

    col_src, col_swap, col_tgt = st.columns([5, 1, 5])

    with col_src:
        src_lang = st.selectbox("Ngôn ngữ nguồn", list(lang_options), key="src_lang")
        src_text = st.text_area("Nhập văn bản nguồn", height=180, key="src_text")
        st.caption(f"{len(src_text)} ký tự")

    with col_swap:
        st.write("")
        st.write("")
        if st.button("⇄", help="Hoán đổi ngôn ngữ"):
            old_src = st.session_state["src_lang"]
            st.session_state["src_lang"] = st.session_state["tgt_lang"]
            st.session_state["tgt_lang"] = old_src
            if st.session_state.get("translated_text"):
                st.session_state["src_text"] = st.session_state["translated_text"]
                st.session_state["translated_text"] = ""
            st.rerun()

    with col_tgt:
        tgt_lang = st.selectbox("Ngôn ngữ đích", list(lang_options), key="tgt_lang")
        st.text_area(
            "Bản dịch",
            value=st.session_state.get("translated_text", ""),
            height=180,
            disabled=True,
        )
        st.caption(f"{len(st.session_state.get('translated_text', ''))} ký tự")

    col_translate, col_clear = st.columns([1, 1])
    with col_translate:
        if st.button("Dịch ngay", type="primary", key="btn_translate"):
            if not src_text.strip():
                st.error("Vui lòng nhập văn bản cần dịch.")
            elif src_lang == tgt_lang:
                st.warning("Vui lòng chọn hai ngôn ngữ khác nhau.")
            else:
                translator = TranslationService()
                with st.spinner("Đang dịch..."):
                    try:
                        st.session_state["translated_text"] = translator.translate(
                            src_text,
                            src=lang_options[src_lang],
                            dest=lang_options[tgt_lang],
                        )
                        st.rerun()
                    except TranslationError as exc:
                        st.error(f"Không thể dịch văn bản: {exc}")

    with col_clear:
        if st.button("Xóa nội dung", key="btn_clear_translate"):
            st.session_state["src_text"] = ""
            st.session_state["translated_text"] = ""
            st.rerun()

# ----------------- TAB 5: ARCHITECTURE & SYSTEM -----------------
with tab_pipeline:
    st.markdown("### ⚙️ Sơ đồ thiết kế hệ thống (Pipeline)")
    st.markdown(
        "Hệ thống **MyTravelHelper** hoạt động dưới dạng một luồng xử lý tuần tự (Sequential Pipeline), "
        "được tối ưu hóa bằng cách kết hợp trí tuệ nhân tạo (Hugging Face Inference Providers) và cơ chế phản hồi dự phòng cục bộ."
    )
    
    st.markdown(
        """
        ```mermaid
        flowchart TD
            A[User Input] --> B[Streamlit UI]
            B --> C{Task Type?}
            C -->|Review text| D[Sentiment Module]
            C -->|Travel query| E[Intent + NER Module]
            C -->|Batch reviews| F[Topic Module]
            D --> G[HF Inference API\ndeberta-v3-absa]
            E --> H[HF Inference API\nbart-large-mnli + bert-NER]
            F --> I[BERTopic\n+ sentence-transformers]
            G --> J[Output Aggregator / Display Helper]
            H --> J
            I --> J
            J --> K[Streamlit Result View\nInteractive Plots & Badges]
        ```
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        #### Các điểm cải tiến nổi bật (Advanced Features):
        1. **Aspect-Based Sentiment Analysis (ABSA):** Không chỉ phân loại tích cực/tiêu cực đơn thuần, mà còn bóc tách chi tiết cảm xúc của khách hàng đối với 9 khía cạnh quan trọng của khách sạn (Vị trí, Dịch vụ, Phòng ốc, Giá cả, Wifi, v.v.).
        2. **Hybrid NER Extraction:** Kết hợp model `bert-base-NER` của Hugging Face và các biểu thức chính quy (Regex) tối ưu để bắt chính xác Địa danh, Thời gian, Khoảng thời gian (Duration) và Ngân sách chuyến đi (Budget).
        3. **Graceful Degradation:** Tự động phát hiện trạng thái kết nối mạng và token Hugging Face để chuyển đổi qua lại giữa API đám mây tốc độ cao và các module fallback cục bộ, giúp ứng dụng không bao giờ bị sập (Zero-downtime).
        """
    )
