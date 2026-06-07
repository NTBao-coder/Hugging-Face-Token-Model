import streamlit as st
import httpx
import json
from pathlib import Path
from utils.display import inject_premium_styles

# Page Config
st.set_page_config(
    page_title="MyTravelHelper — Dịch vụ du lịch",
    page_icon="✈️",
    layout="wide"
)

inject_premium_styles()

BACKEND_URL = "http://localhost:8000"

st.markdown(
    """
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1 style='color:#000000; margin-bottom: 5px; font-family: "Nunito", sans-serif;'>✈️ Dịch Vụ Du Lịch</h1>
        <p style='color:#737373; font-size:1rem;'>Lựa chọn khách sạn nghỉ dưỡng, tour du lịch trọn gói hoặc vé máy bay cho hành trình của bạn</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Load Services from JSON
CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
SERVICES_PATH = CONFIG_DIR / "services.json"

services = []
if SERVICES_PATH.exists():
    with open(SERVICES_PATH, "r", encoding="utf-8") as f:
        services = json.load(f)
else:
    st.error("Không tìm thấy file cấu hình dịch vụ tại config/services.json")

# Display login banner
is_logged_in = "user_token" in st.session_state and st.session_state["user_token"] is not None

if not is_logged_in:
    st.warning("⚠️ Bạn chưa đăng nhập. Vui lòng đăng nhập để thực hiện đặt dịch vụ và thanh toán.")
    if st.button("Đi tới trang Đăng nhập / Đăng ký", type="primary"):
        # Streamlit doesn't support direct redirect to another page programmatically via url,
        # but we can instruct the user or display links. Multipage sidebar is visible to redirect them.
        st.info("Hãy click chọn mục **1 Auth** ở danh sách trang bên trái để đăng nhập.")
else:
    user = st.session_state["user_info"]
    st.info(f"👤 Tài khoản đặt mua: **{user.get('email')}**")

# Category filter
categories = ["Tất cả", "Hotel Booking", "Tour", "Flight"]
selected_category = st.selectbox("Lọc theo loại dịch vụ:", categories)

filtered_services = [
    s for s in services 
    if selected_category == "Tất cả" or s["category"] == selected_category
]

# Grid display
if filtered_services:
    for service in filtered_services:
        with st.container():
            st.markdown(
                f"""
                <div class="glass-card" style="margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <span style="background: #fafafa; color: #000000; padding: 4px 12px; border-radius: 9999px; font-size: 0.8rem; font-weight: 500; border: 1px solid #e5e5e5; font-family: ui-monospace, monospace;">
                                {service['category']}
                            </span>
                            <h3 style="margin: 14px 0 5px 0; color: #000000;">{service['name']}</h3>
                            <p style="margin: 0; color: #a3a3a3; font-size: 0.9rem;">📍 {service['location']}</p>
                            <p style="margin: 10px 0 0 0; color: #737373; font-size: 0.95rem;">{service['description']}</p>
                        </div>
                        <div style="text-align: right; min-width: 150px; margin-top: 10px;">
                            <div style="font-size: 0.85rem; color: #a3a3a3;">Giá tiền</div>
                            <div style="font-size: 1.6rem; font-weight: 700; color: #000000; margin-bottom: 10px;">
                                {service['price']:,.0f} VND
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Booking button (using a standard columns for alignment)
            col_left, col_btn = st.columns([5, 1])
            with col_btn:
                if is_logged_in:
                    # Unique key for button
                    btn_key = f"btn_book_{service['id']}"
                    if st.button("Đặt ngay 🛒", key=btn_key, use_container_width=True, type="primary"):
                        with st.spinner("Đang tạo đơn hàng..."):
                            try:
                                headers = {"Authorization": f"Bearer {st.session_state['user_token']}"}
                                payload = {
                                    "service_type": "hotel_booking" if service["category"] == "Hotel Booking" else service["category"].lower(),
                                    "service_name": service["name"],
                                    "amount": float(service["price"])
                                }
                                response = httpx.post(
                                    f"{BACKEND_URL}/api/orders/create", 
                                    json=payload, 
                                    headers=headers,
                                    timeout=10.0
                                )
                                
                                if response.status_code == 200:
                                    order = response.json()
                                    st.session_state["current_order"] = order
                                    st.success(f"🎉 Đã đặt thành công! Mã đơn: **{order['order_id']}**")
                                    st.info("Nhấp vào **3 Payment** trong menu bên trái để tiến hành thanh toán.")
                                else:
                                    st.error(f"Lỗi đặt dịch vụ: {response.text}")
                            except Exception as e:
                                st.error(f"Không thể kết nối backend: {e}")
                else:
                    st.button("Đặt ngay 🛒", key=f"btn_disabled_{service['id']}", disabled=True, use_container_width=True)
            st.markdown("---")
else:
    st.info("Không tìm thấy dịch vụ nào phù hợp.")
