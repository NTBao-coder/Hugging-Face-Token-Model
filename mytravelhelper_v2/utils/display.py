"""Streamlit display and visualization styling utilities."""

import streamlit as st
import pandas as pd

try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


def inject_premium_styles() -> None:
    """Inject modern premium styles, custom Google Fonts, and glassmorphism elements."""
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        
        <style>
        /* Base typography */
        html, body, [class*="css"], .stMarkdown {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }
        
        /* Main title styling */
        .main-title {
            background: linear-gradient(135deg, #FF4B4B 0%, #FF8F6B 50%, #4B6BFF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem !important;
            font-weight: 800 !important;
            margin-bottom: 0.1rem;
            text-shadow: 0px 4px 20px rgba(255, 75, 75, 0.15);
        }
        
        /* Custom cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .glass-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.08);
            border-color: rgba(255, 255, 255, 0.2);
        }
        
        /* Sidebar layout */
        .css-1542moe, [data-testid="stSidebar"] {
            background-color: #0F111A;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* Badge styling */
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.8rem;
            margin: 2px;
        }
        .badge-positive {
            background-color: rgba(46, 204, 113, 0.15);
            color: #2ecc71;
            border: 1px solid rgba(46, 204, 113, 0.3);
        }
        .badge-negative {
            background-color: rgba(231, 76, 60, 0.15);
            color: #e74c3c;
            border: 1px solid rgba(231, 76, 60, 0.3);
        }
        .badge-neutral {
            background-color: rgba(149, 165, 166, 0.15);
            color: #95a5a6;
            border: 1px solid rgba(149, 165, 166, 0.3);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def render_main_title() -> None:
    """Render the main header of the application."""
    st.markdown('<h1 class="main-title">🌏 MyTravelHelper</h1>', unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:1.15rem; color:#8A90A6; margin-top:-0.5rem; margin-bottom:2rem;'>"
        "Trợ lý NLP & LLM nâng cao phân tích cảm xúc khía cạnh, ý định du lịch và tự động gom cụm chủ đề."
        "</p>",
        unsafe_allow_html=True,
    )

def show_aspect_sentiment_grid(aspects: list[dict]) -> None:
    """Render aspect sentiment scores as beautiful cards in a grid."""
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
            text_color = "#2ecc71"
            bg_color = "rgba(46, 204, 113, 0.05)"
        elif sentiment_en in ["NEGATIVE", "TIÊU CỰC"]:
            badge_class = "badge-negative"
            text_color = "#e74c3c"
            bg_color = "rgba(231, 76, 60, 0.05)"
        else:
            badge_class = "badge-neutral"
            text_color = "#95a5a6"
            bg_color = "rgba(149, 165, 166, 0.05)"
            
        with col:
            st.markdown(
                f"""
                <div style="background:{bg_color}; border-radius:12px; padding:16px; border: 1px solid rgba(255,255,255,0.05); margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:700; font-size:1.05rem;">{aspect_name}</span>
                        <span class="badge {badge_class}">{sentiment_vi}</span>
                    </div>
                    <div style="margin-top:10px; font-size:0.85rem; color:#8A90A6;">
                        Độ tin cậy: <span style="color:{text_color}; font-weight:600;">{score:.2f}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

def render_entity_badges(entities: list[dict]) -> None:
    """Render named entities inside markdown badges."""
    if not entities:
        st.write("Không tìm thấy thực thể nào.")
        return

    badges_html = []
    type_color_map = {
        "LOCATION": "#4B6BFF",
        "LOC": "#4B6BFF",
        "DATE": "#FF8F6B",
        "DURATION": "#2ecc71",
        "BUDGET": "#F1C40F",
        "PER": "#9B59B6",
        "ORG": "#34495E"
    }

    for ent in entities:
        val = ent.get("text") or ent.get("word") or "unknown"
        etype = ent.get("entity_type") or ent.get("type") or "UNKNOWN"
        etype_vi = ent.get("entity_type_vi", etype)
        color = type_color_map.get(etype.upper(), "#95a5a6")
        
        badges_html.append(
            f'<span style="display:inline-block; background:rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.15); '
            f'color:{color}; border: 1px solid {color}4D; padding:4px 10px; border-radius:8px; margin:4px; font-weight:600; font-size:0.9rem;">'
            f'{val} <span style="font-size:0.7rem; font-weight:400; opacity:0.8;">({etype_vi})</span>'
            f'</span>'
        )
    
    st.markdown(" ".join(badges_html), unsafe_allow_html=True)

def show_topic_bar_chart(df_topics: pd.DataFrame) -> None:
    """Display an elegant Plotly bar chart for topics and counts or fallback to Streamlit's native bar chart."""
    df = df_topics.copy()
    
    # Resolve the count column (case-insensitive)
    count_col = None
    for c in df.columns:
        if str(c).lower() == "count":
            count_col = c
            break
            
    # Resolve the label/topic name column (prioritize 'Name', 'name', or 'topic' that isn't the integer ID)
    label_col = None
    for c in df.columns:
        if str(c).lower() in ["name", "label"]:
            label_col = c
            break
            
    if label_col is None:
        for c in df.columns:
            if str(c) == "topic":  # Lowercase renamed topic
                label_col = c
                break
                
    if label_col is None:
        for c in df.columns:
            if str(c).lower() == "topic":
                label_col = c
                break
                
    # Fallback to the first column that isn't the count column
    if label_col is None and count_col is not None:
        remaining = [c for c in df.columns if c != count_col]
        if remaining:
            label_col = remaining[0]
            
    if count_col is None or label_col is None:
        st.warning("Không thể trích xuất cột dữ liệu vẽ biểu đồ.")
        return
        
    # Reconstruct a clean, duplicate-free, explicitly-typed DataFrame
    viz_df = pd.DataFrame({
        "topic": df[label_col].astype(str),
        "count": df[count_col].astype(int)
    })
    
    if HAS_PLOTLY:
        fig = px.bar(
            viz_df,
            x="count",
            y="topic",
            orientation="h",
            color="count",
            color_continuous_scale=px.colors.sequential.Sunsetdark,
            labels={"count": "Số lượng review", "topic": "Chủ đề"},
            title="Phân bố các chủ đề phát hiện được"
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_family="Plus Jakarta Sans",
            font_color="#E4E6EB",
            title_font_family="Outfit",
            title_font_size=18,
            xaxis_showgrid=True,
            xaxis_gridcolor="rgba(255,255,255,0.05)",
            yaxis_showgrid=False,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Fallback to streamlit native bar chart
        st.info("💡 Mách nhỏ: Cài đặt `plotly` (`pip install plotly`) để xem biểu đồ tương tác đẹp mắt hơn.")
        chart_df = viz_df.set_index("topic")
        st.bar_chart(chart_df)



