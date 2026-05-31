"""Streamlit application for MyTravelHelper - AI-powered travel assistant (v2.0 Multilingual)."""

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
from modules.topic import detect_topics_bertopic
from modules.translation import TranslationService

# Initialize Translation Service
translator = TranslationService()

# Set page configuration
st.set_page_config(
    page_title="MyTravelHelper — AI Assistant v2.0",
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
            <p style='color:#8A90A6; font-size:0.85rem;'>Phiên bản 2.0.0 (Multilingual)</p>
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
    
    st.subheader("Mô hình sử dụng (v2.0)")
    st.markdown(
        """
        - **Dịch thuật:** `Google Translate API / googletrans`
        - **Phát hiện ngôn ngữ:** `langdetect`
        - **Chat/NLU:** `Mistral-7B-Instruct-v0.2` (via Translation wrapper)
        - **Intent classification:** `BART-large-mnli` (via Translation wrapper)
        - **Named Entity Recognition:** `BERT-base-NER` + Heuristics
        - **Aspect Sentiment:** `DeBERTa-v3-base-absa-v1.1`
        - **Topic Clustering:** `BERTopic` / `KMeans` + `BART-large-mnli`
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
    st.markdown(
        "Nhập câu hỏi hoặc yêu cầu du lịch bằng **tiếng Việt 🇻🇳** hoặc **tiếng Anh 🇺🇸**. "
        "Hệ thống tự động phát hiện ngôn ngữ, chạy mô hình NLU và phản hồi song ngữ/dịch tương ứng."
    )
    
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
                # Detect Language
                lang_code, lang_conf = translator.detect_language(user_query)
                lang_name = "Tiếng Việt 🇻🇳" if lang_code == "vi" else "Tiếng Anh 🇺🇸"
                
                # If Vietnamese, translate to English for NLU models
                translated_query = user_query
                if lang_code == "vi":
                    try:
                        translated_query = translator.translate(user_query, src="vi", dest="en")
                    except Exception:
                        pass
                
                # 1. Classify Intent
                intent_res = classify_intent(user_query)
                intent_en = intent_res["intent"]
                intent_vi = intent_res.get("intent_vi", intent_en)
                
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
            
            # Bilingual view details if VI
            if lang_code == "vi":
                with st.expander("🌐 Xem chi tiết bản dịch hệ thống"):
                    st.write(f"**Ngôn ngữ phát hiện:** {lang_name} (Độ tin cậy: {lang_conf:.2f})")
                    st.write(f"**Văn bản dịch (EN):** _{translated_query}_")
            
            st.markdown("#### 🔍 Kết quả phân tích Ngôn ngữ tự nhiên (NLU):")
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
    st.markdown("Nhập review bằng **tiếng Việt 🇻🇳** hoặc **tiếng Anh 🇺🇸** để phân tích cảm xúc chung và chi tiết khía cạnh.")
    
    sample_option = st.radio("Chọn ngôn ngữ review mẫu:", ["Tiếng Việt 🇻🇳", "Tiếng Anh 🇺🇸"], horizontal=True)
    
    if sample_option == "Tiếng Việt 🇻🇳":
        sample_reviews = [
            "Khách sạn có phòng sạch sẽ, nhân viên lễ tân cực kỳ thân thiện và chu đáo.",
            "Vị trí rất đắc địa, chỉ mất 2 phút đi bộ ra bãi tắm Mỹ Khê. Tuy nhiên giá phòng hơi đắt.",
            "Đồ ăn sáng nghèo nàn, wifi trong phòng hầu như không bắt được sóng, rất thất vọng.",
            "Custom"
        ]
    else:
        sample_reviews = [
            "The hotel is clean, location is perfect right next to the beach, but service is slow.",
            "The room was spacious but wifi was extremely weak. Price is too high.",
            "Great breakfast buffet and very friendly reception staff.",
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
                lang_code, _ = translator.detect_language(review_input)
                
                # Run basic sentiment
                overall = analyze_sentiment(review_input, mode="basic")
                # Run aspect sentiment (ABSA)
                aspects = analyze_sentiment(review_input, mode="absa")
                
            st.markdown("#### Kết quả phân tích:")
            
            # Display overall metric
            color_map = {"POSITIVE": "#2ecc71", "NEGATIVE": "#e74c3c", "NEUTRAL": "#95a5a6"}
            lbl = overall.get("label", "NEUTRAL")
            lbl_vi = overall.get("label_vi", lbl)
            clr = color_map.get(lbl, "#95a5a6")
            
            st.markdown(
                f"""
                <div style='background:rgba(255,255,255,0.03); border-radius:12px; padding:20px; border:1px solid rgba(255,255,255,0.05); margin-bottom:20px; display:inline-block;'>
                    <div style='font-size:0.9rem; color:#8A90A6;'>Cảm xúc tổng thể</div>
                    <div style='font-size:2rem; font-weight:800; color:{clr};'>{lbl_vi} ({lbl})</div>
                    <div style='font-size:0.85rem; color:#8A90A6; margin-top:5px;'>
                        Độ tin cậy: <strong>{overall.get('score', 0.0):.2f}</strong> ({overall.get('source', '')})
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Bilingual details
            if lang_code == "vi" and overall.get("translated_text"):
                st.info(f"🌐 **Bản dịch hệ thống (EN):** _{overall['translated_text']}_")
                
            st.markdown("#### Cảm xúc chi tiết theo từng khía cạnh:")
            show_aspect_sentiment_grid(aspects)

# ----------------- TAB 3: TOPIC MODELING -----------------
with tab_topic:
    st.markdown("### 🏷️ Gom cụm chủ đề từ nhiều review (Topic Detection)")
    st.markdown("Tải hoặc nhập tập hợp đánh giá để gom cụm chủ đề bằng tiếng Việt hoặc tiếng Anh.")
    
    data_option = st.radio("Nguồn dữ liệu review:", ["Dùng review mẫu Tiếng Việt 🇻🇳", "Dùng review mẫu Tiếng Anh 🇺🇸", "Nhập danh sách review thủ công"], horizontal=True)
    
    reviews_to_run = []
    
    if data_option == "Dùng review mẫu Tiếng Việt 🇻🇳":
        sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_reviews_vi.json")
        if os.path.exists(sample_path):
            with open(sample_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                reviews_to_run = [r["text"] for r in data]
            st.info(f"Đã load {len(reviews_to_run)} review mẫu từ file `data/sample_reviews_vi.json`.")
            with st.expander("Xem trước danh sách review mẫu"):
                st.write(reviews_to_run)
        else:
            st.error("Không tìm thấy file `data/sample_reviews_vi.json`.")
    elif data_option == "Dùng review mẫu Tiếng Anh 🇺🇸":
        sample_path = os.path.join(os.path.dirname(__file__), "unmodified_v1", "sample_reviews.json")
        if not os.path.exists(sample_path):
            sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_reviews.json")
            
        if os.path.exists(sample_path):
            with open(sample_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                reviews_to_run = [r["text"] for r in data]
            st.info(f"Đã load {len(reviews_to_run)} review mẫu.")
            with st.expander("Xem trước danh sách review mẫu"):
                st.write(reviews_to_run)
        else:
            st.error(f"Không tìm thấy file review mẫu tiếng Anh.")
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
        if len(reviews_to_run) < 2:
            st.error("Cần ít nhất 2 review để chạy thuật toán gom cụm chủ đề.")
        else:
            with st.spinner("Đang chạy embedding và mô hình gom cụm... (Vui lòng đợi vài giây)"):
                topics, model = detect_topics_bertopic(reviews_to_run)
                
            st.markdown("#### Kết quả gom cụm:")
            
            try:
                topic_info = model.get_topic_info()
            except Exception as e:
                st.error(f"Lỗi khi đọc thông tin chủ đề: {e}")
                topic_info = pd.DataFrame()
                
            if not topic_info.empty:
                col_table, col_chart = st.columns([1, 1])
                
                with col_table:
                    st.markdown("##### Bảng thống kê chủ đề")
                    display_df = topic_info.copy()
                    if "Representation" in display_df.columns:
                        display_df["Representation"] = display_df["Representation"].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                    
                with col_chart:
                    st.markdown("##### Biểu đồ phân bố chủ đề")
                    chart_df = topic_info[topic_info["Topic"] != -1].copy()
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
                    words_df = pd.DataFrame(rep_words, columns=["Từ khóa", "Trọng số TF-IDF / Trọng số centroids"])
                    st.dataframe(words_df, use_container_width=True, hide_index=True)
                else:
                    st.info("Chủ đề này không có từ khóa đại diện riêng lẻ.")
            else:
                st.warning("Không phát hiện được chủ đề nào rõ rệt từ tập review.")

# ----------------- TAB 4: TRANSLATION TOOL -----------------
with tab_translate:
    st.markdown("### 🌐 Công cụ Dịch thuật tự do English ↔ Vietnamese")
    st.markdown("Dịch thuật văn bản tự do nhanh chóng. Hỗ trợ hoán đổi ngôn ngữ thông minh.")
    
    # Check session states for swap logic
    if "src_lang" not in st.session_state:
        st.session_state["src_lang"] = "Tiếng Việt 🇻🇳"
    if "tgt_lang" not in st.session_state:
        st.session_state["tgt_lang"] = "Tiếng Anh 🇺🇸"
    if "src_text" not in st.session_state:
        st.session_state["src_text"] = ""
    if "translated_text" not in st.session_state:
        st.session_state["translated_text"] = ""
        
    col1, col_swap, col2 = st.columns([5, 1, 5])
    
    with col1:
        src_lang = st.selectbox(
            "Ngôn ngữ nguồn",
            ["Tiếng Việt 🇻🇳", "Tiếng Anh 🇺🇸"],
            key="src_lang"
        )
        src_text = st.text_area("Nhập văn bản nguồn:", height=180, key="src_text")
        
    with col_swap:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("⇄", help="Hoán đổi ngôn ngữ", key="btn_swap"):
            # Swap languages
            old_src = st.session_state["src_lang"]
            st.session_state["src_lang"] = st.session_state["tgt_lang"]
            st.session_state["tgt_lang"] = old_src
            
            # Swap texts
            old_src_text = st.session_state["src_text"]
            st.session_state["src_text"] = st.session_state["translated_text"]
            st.session_state["translated_text"] = old_src_text
            st.rerun()
            
    with col2:
        tgt_lang = st.selectbox(
            "Ngôn ngữ đích",
            ["Tiếng Anh 🇺🇸", "Tiếng Việt 🇻🇳"],
            key="tgt_lang"
        )
        # Disable editing on translation output, read from translated_text
        st.text_area("Bản dịch:", value=st.session_state["translated_text"], height=180, disabled=True)
        
    if st.button("🌐 Dịch ngay", type="primary", key="btn_translate_now"):
        if not st.session_state["src_text"].strip():
            st.error("Vui lòng nhập văn bản cần dịch.")
        else:
            with st.spinner("Đang tiến hành dịch thuật..."):
                src_code = "vi" if "Việt" in st.session_state["src_lang"] else "en"
                tgt_code = "en" if "Anh" in st.session_state["tgt_lang"] else "vi"
                try:
                    result = translator.translate(st.session_state["src_text"], src=src_code, dest=tgt_code)
                    st.session_state["translated_text"] = result
                    st.rerun()
                except Exception as e:
                    st.error(f"Dịch thất bại: {e}")

# ----------------- TAB 5: ARCHITECTURE & SYSTEM -----------------
with tab_pipeline:
    st.markdown("### ⚙️ Sơ đồ thiết kế hệ thống v2.0 (Pipeline)")
    st.markdown(
        "Hệ thống **MyTravelHelper v2.0** tích hợp thêm lớp ngôn ngữ (Language Layer) "
        "được tối ưu hóa bằng cách kết hợp trí tuệ nhân tạo (Hugging Face Inference Providers) và cơ chế phản hồi dự phòng cục bộ."
    )
    
    st.markdown(
        """
        ```mermaid
        flowchart TD
            A[User Input\nVI hoặc EN] --> B[Language Detection\nlangdetect]
            B -->|Tiếng Việt| C[★ Google Translate\nVI → EN]
            B -->|Tiếng Anh| D[Bypass Translation]
            C --> E[English Text]
            D --> E
            E --> F{Task Type?}
            F -->|Review| G[Sentiment/ABSA\ndeberta-v3-absa]
            F -->|Query| H[Intent + NER\nbart-mnli + bert-NER]
            F -->|Batch docs| I[Topic Detection\nBERTopic + bart-mnli]
            G --> J[★ Result Translator\nlabel_mapper.py]
            H --> J
            I --> J
            J --> K[★ Bilingual Display\nEN + VI side by side]

            L[Tab 4: Translation Tool] --> M[★ TranslationService\ngoogletrans wrapper]
            M -->|EN→VI| N[Vietnamese Output]
            M -->|VI→EN| O[English Output]
            N --> P[★ Swap Button ⇄]
            O --> P
            P --> M

            style C fill:#fef3c7,stroke:#d97706
            style J fill:#fef3c7,stroke:#d97706
            style L fill:#dbeafe,stroke:#2563eb
            style M fill:#dbeafe,stroke:#2563eb
            style P fill:#dbeafe,stroke:#2563eb
        ```
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        #### Các điểm nâng cấp nổi bật ở v2.0:
        1. **Chiến lược "Translate-then-Process":** Tự động phát hiện và dịch thuật ngôn ngữ đầu vào tiếng Việt sang tiếng Anh trước khi đưa qua mô hình, giúp tái sử dụng hoàn hảo các mô hình NLP tiếng Anh chất lượng cao.
        2. **Dịch nhãn đầu ra song ngữ:** Tự động tra cứu và dịch các khía cạnh (room -> phòng ốc, cleanliness -> vệ sinh) và các trạng thái cảm xúc, ý định sang tiếng Việt thân thiện với người dùng.
        3. **Giải pháp fallback dịch thuật thông minh:** Hệ thống kết hợp nhiều công cụ dịch thuật (`googletrans`, `deep-translator` GoogleTranslator) để đảm bảo độ bền vững cao nhất khi gọi API.
        4. **Name Preservation:** Đối với trích xuất thực thể (NER), hệ thống ánh xạ vị trí địa danh và tiền tệ ngược từ tiếng Anh dịch lại đúng cụm từ gốc tiếng Việt, bảo toàn các ký tự có dấu như "Đà Nẵng", "Phú Quốc".
        """
    )
