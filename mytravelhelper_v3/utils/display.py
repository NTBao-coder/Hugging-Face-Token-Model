"""Streamlit display and visualization styling utilities following Ollama-design guidelines."""

import streamlit as st
import pandas as pd

try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


def inject_premium_styles() -> None:
    """Inject minimal paper-white canvas styling, custom Google Fonts, and black pill buttons."""
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
        
        <style>
        /* Base typography & Canvas color */
        html, body, [class*="css"], .stMarkdown {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #737373 !important; /* body text default */
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Nunito', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #000000 !important;
            font-weight: 600 !important;
            letter-spacing: -0.01em;
        }
        
        /* Force light background for canvas */
        .stApp {
            background-color: #ffffff !important;
            color: #737373 !important;
        }
        
        /* Main title styling */
        .main-title {
            font-family: 'Nunito', sans-serif !important;
            color: #000000 !important;
            font-size: 36px !important;
            font-weight: 700 !important;
            margin-bottom: 8px !important;
        }
        
        /* Flat paper-white cards with hairline border */
        .glass-card {
            background: #ffffff !important;
            border-radius: 12px !important;
            padding: 24px !important;
            border: 1px solid #e5e5e5 !important;
            box-shadow: none !important;
            margin-bottom: 20px !important;
            transition: border-color 0.15s ease !important;
            color: #737373 !important;
        }
        .glass-card:hover {
            border-color: #d4d4d4 !important;
        }
        .glass-card h1, .glass-card h2, .glass-card h3, .glass-card h4, .glass-card h5, .glass-card h6 {
            color: #000000 !important;
            margin-top: 0;
        }
        
        /* Sidebar styling - soft gray background with hairline right border */
        [data-testid="stSidebar"] {
            background-color: #fafafa !important;
            border-right: 1px solid #e5e5e5 !important;
        }
        [data-testid="stSidebar"] * {
            color: #000000 !important;
        }
        [data-testid="stSidebarNav"] {
            background-color: transparent !important;
        }
        
        /* Override Streamlit Buttons to be black pills */
        div.stButton > button {
            background-color: #000000 !important;
            color: #ffffff !important;
            border-radius: 9999px !important; /* rounded full */
            border: 1px solid #000000 !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            padding: 8px 24px !important;
            height: 38px !important;
            box-shadow: none !important;
            transition: background-color 0.15s ease, border-color 0.15s ease !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        div.stButton > button:hover {
            background-color: #171717 !important;
            border-color: #171717 !important;
            color: #ffffff !important;
        }
        div.stButton > button:active {
            background-color: #262626 !important;
            border-color: #262626 !important;
        }
        
        /* Secondary outlines for specific buttons */
        div.stButton > button[key*="secondary"], div.stButton > button[key*="logout"], div.stButton > button[key*="swap"] {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #d4d4d4 !important;
        }
        div.stButton > button[key*="secondary"]:hover, div.stButton > button[key*="logout"]:hover, div.stButton > button[key*="swap"]:hover {
            background-color: #fafafa !important;
            border-color: #a3a3a3 !important;
            color: #000000 !important;
        }
        
        /* Form inputs styled as pills */
        div.stTextInput input, div.stNumberInput input, div.stSelectbox div[data-baseweb="select"] {
            border-radius: 9999px !important; /* rounded full */
            border: 1px solid #e5e5e5 !important;
            background-color: #ffffff !important;
            color: #000000 !important;
            padding: 6px 16px !important;
            height: 40px !important;
            box-shadow: none !important;
        }
        div.stTextInput input:focus, div.stNumberInput input:focus {
            border-color: #000000 !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important; /* Focus ring */
        }
        
        /* Textareas styled as soft boxes */
        div.stTextArea textarea {
            border-radius: 12px !important; /* rounded lg */
            border: 1px solid #e5e5e5 !important;
            background-color: #ffffff !important;
            color: #000000 !important;
            padding: 12px 16px !important;
            box-shadow: none !important;
        }
        div.stTextArea textarea:focus {
            border-color: #000000 !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
        }
        
        /* Badge pill layout */
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 9999px; /* rounded full */
            font-weight: 600;
            font-size: 0.8rem;
            margin: 2px;
        }
        .badge-positive {
            background-color: rgba(39, 201, 63, 0.08) !important;
            color: #27c93f !important;
            border: 1px solid rgba(39, 201, 63, 0.2) !important;
        }
        .badge-negative {
            background-color: rgba(255, 95, 86, 0.08) !important;
            color: #ff5f56 !important;
            border: 1px solid rgba(255, 95, 86, 0.2) !important;
        }
        .badge-neutral {
            background-color: rgba(255, 189, 46, 0.08) !important;
            color: #ffbd2e !important;
            border: 1px solid rgba(255, 189, 46, 0.2) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_main_title() -> None:
    """Render the center-aligned hero title of the application."""
    st.markdown(
        """
        <div style="text-align: center; margin-top: 30px; margin-bottom: 24px;">
            <div style="font-size: 64px; margin-bottom: 12px; filter: grayscale(100%);">🌏</div>
            <h1 class="main-title" style="margin: 0; font-family: 'Nunito', sans-serif;">MyTravelHelper</h1>
            <p style="font-size: 16px; color: #737373; margin-top: 8px; margin-bottom: 24px; font-family: 'Inter', sans-serif; max-width: 720px; margin-left: auto; margin-right: auto;">
                Trợ lý NLP & LLM phân tích cảm xúc khía cạnh, trích xuất thực thể, phát hiện ý định và gom cụm chủ đề review du lịch đa ngôn ngữ.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_aspect_sentiment_grid(aspects: list[dict]) -> None:
    """Render aspect sentiment scores as flat card elements in a grid."""
    if not aspects:
        st.info("Chưa có thông tin khía cạnh nào được nhận dạng.")
        return

    # Create Columns
    cols = st.columns(min(3, len(aspects)))
    for idx, item in enumerate(aspects):
        col = cols[idx % len(cols)]
        aspect_name = item.get("aspect_vi", item.get("aspect", "")).capitalize()
        sentiment_vi = item.get("sentiment_vi", item.get("sentiment", "NEUTRAL")).upper()
        sentiment_en = item.get("sentiment", "NEUTRAL").upper()
        score = item.get("confidence", 0.0)
        
        # Color classes based on English sentiment key
        if sentiment_en in ["POSITIVE", "TÍCH CỰC"]:
            badge_class = "badge-positive"
            text_color = "#27c93f"
            bg_color = "rgba(39, 201, 63, 0.03)"
        elif sentiment_en in ["NEGATIVE", "TIÊU CỰC"]:
            badge_class = "badge-negative"
            text_color = "#ff5f56"
            bg_color = "rgba(255, 95, 86, 0.03)"
        else:
            badge_class = "badge-neutral"
            text_color = "#ffbd2e"
            bg_color = "rgba(255, 189, 46, 0.03)"
            
        with col:
            st.markdown(
                f"""
                <div style="background:{bg_color}; border-radius:12px; padding:16px; border: 1px solid #e5e5e5; margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:600; font-size:1rem; color: #000000;">{aspect_name}</span>
                        <span class="badge {badge_class}">{sentiment_vi}</span>
                    </div>
                    <div style="margin-top:10px; font-size:0.85rem; color:#a3a3a3;">
                        Độ tin cậy: <span style="color:{text_color}; font-weight:600;">{score:.2f}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


def render_entity_badges(entities: list[dict]) -> None:
    """Render named entities inside command-tag styled badges."""
    if not entities:
        st.write("Không tìm thấy thực thể nào.")
        return

    badges_html = []
    for ent in entities:
        val = ent.get("text") or ent.get("word") or "unknown"
        etype = ent.get("entity_type") or ent.get("type") or "UNKNOWN"
        etype_vi = ent.get("entity_type_vi", etype)
        
        badges_html.append(
            f'<span style="display:inline-block; background:#fafafa; color:#000000; '
            f'border: 1px solid #e5e5e5; padding:6px 12px; border-radius:9999px; margin:4px; '
            f'font-family: ui-monospace, monospace; font-size:0.85rem; font-weight: 500;">'
            f'{val} <span style="font-size:0.7rem; color:#a3a3a3; font-weight:400;">({etype_vi})</span>'
            f'</span>'
        )
    
    st.markdown(" ".join(badges_html), unsafe_allow_html=True)


def show_topic_bar_chart(df_topics: pd.DataFrame) -> None:
    """Display a high-contrast minimalist horizontal bar chart matching brand colors."""
    df = df_topics.copy()
    
    # Resolve the count column
    count_col = None
    for c in df.columns:
        if str(c).lower() == "count":
            count_col = c
            break
            
    # Resolve the label/topic name column
    label_col = None
    for c in df.columns:
        if str(c).lower() in ["name", "label"]:
            label_col = c
            break
            
    if label_col is None:
        for c in df.columns:
            if str(c) == "topic":
                label_col = c
                break
                
    if label_col is None:
        for c in df.columns:
            if str(c).lower() == "topic":
                label_col = c
                break
                
    if label_col is None and count_col is not None:
        remaining = [c for c in df.columns if c != count_col]
        if remaining:
            label_col = remaining[0]
            
    if count_col is None or label_col is None:
        st.warning("Không thể trích xuất cột dữ liệu vẽ biểu đồ.")
        return
        
    viz_df = pd.DataFrame({
        "topic": df[label_col].astype(str),
        "count": df[count_col].astype(int)
    })
    
    if HAS_PLOTLY:
        # High contrast minimal horizontal bar chart
        fig = px.bar(
            viz_df,
            x="count",
            y="topic",
            orientation="h",
            labels={"count": "Số lượng review", "topic": "Chủ đề"},
            title="Phân bố các chủ đề phát hiện được",
            color_discrete_sequence=["#000000"] # Pure black bars matching primary brand color
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_family="Inter",
            font_color="#737373",
            title_font_family="Nunito",
            title_font_size=18,
            xaxis_showgrid=True,
            xaxis_gridcolor="#e5e5e5",
            yaxis_showgrid=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("💡 Mách nhỏ: Cài đặt `plotly` (`pip install plotly`) để xem biểu đồ tương tác đẹp mắt hơn.")
        chart_df = viz_df.set_index("topic")
        st.bar_chart(chart_df)
