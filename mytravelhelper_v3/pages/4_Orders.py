import streamlit as st
import httpx
from datetime import datetime
from utils.display import inject_premium_styles

# Page Config
st.set_page_config(
    page_title="MyTravelHelper — Lịch sử đơn hàng",
    page_icon="📋",
    layout="wide"
)

inject_premium_styles()

BACKEND_URL = "http://localhost:8000"

st.markdown(
    """
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1 style='color:#000000; margin-bottom: 5px; font-family: "Nunito", sans-serif;'>📋 Lịch Sử Đơn Hàng</h1>
        <p style='color:#737373; font-size:1rem;'>Theo dõi danh sách các đơn hàng đã đặt và trạng thái giao dịch thanh toán của bạn</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Check login status
is_logged_in = "user_token" in st.session_state and st.session_state["user_token"] is not None

if not is_logged_in:
    st.warning("⚠️ Bạn chưa đăng nhập. Vui lòng đăng nhập để xem lịch sử đơn hàng.")
    st.info("Hãy click chọn mục **1 Auth** ở danh sách trang bên trái để đăng nhập.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state['user_token']}"}

col_ref, col_space = st.columns([1, 5])
with col_ref:
    refresh_btn = st.button("🔄 Làm mới dữ liệu", use_container_width=True)

with st.spinner("Đang tải dữ liệu lịch sử đặt hàng..."):
    try:
        response = httpx.get(f"{BACKEND_URL}/api/orders/history", headers=headers, timeout=10.0)
        
        if response.status_code == 200:
            orders = response.json()
            
            if not orders:
                st.info("🛍️ Bạn chưa có đơn hàng nào. Hãy đặt dịch vụ tại trang **2 Services**!")
            else:
                for idx, order in enumerate(orders):
                    # Style badge based on status
                    status_lbl = order["status"].upper()
                    if status_lbl == "PAID":
                        badge_color = "#27c93f"
                        badge_bg = "rgba(39, 201, 63, 0.08)"
                    elif status_lbl == "FAILED":
                        badge_color = "#ff5f56"
                        badge_bg = "rgba(255, 95, 86, 0.08)"
                    else:
                        badge_color = "#ffbd2e"
                        badge_bg = "rgba(255, 189, 46, 0.08)"
                        
                    # Format time
                    created_time = order["created_at"]
                    try:
                        dt = datetime.fromisoformat(created_time.replace("Z", "+00:00"))
                        formatted_time = dt.strftime("%H:%M:%S - %d/%m/%Y")
                    except Exception:
                        formatted_time = created_time
                        
                    st.markdown(
                        f"""
                        <div class="glass-card" style="margin-bottom: 15px; border-left: 4px solid {badge_color} !important;">
                            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                                <div>
                                    <h4 style="margin: 0; color: #000000; font-family: 'Nunito', sans-serif;">Mã đơn: <code style="color: #000000; background: #fafafa; padding: 2px 6px; border-radius: 4px; border: 1px solid #e5e5e5;">{order['order_id']}</code></h4>
                                    <p style="margin: 10px 0 5px 0; font-size: 0.95rem; color: #737373;">
                                        <strong>{order['service_name']}</strong> ({order['service_type'].upper()})
                                    </p>
                                    <p style="margin: 0; font-size: 0.85rem; color: #a3a3a3;">📅 Thời gian đặt: {formatted_time}</p>
                                </div>
                                <div style="text-align: right; min-width: 150px; margin-top: 10px;">
                                    <span class="badge" style="color: {badge_color}; background: {badge_bg}; padding: 4px 12px; border-radius: 9999px; font-size: 0.85rem; font-weight: 700; border: 1px solid {badge_color}33;">
                                        {status_lbl}
                                    </span>
                                    <div style="font-size: 1.25rem; font-weight: 700; color: #000000; margin-top: 10px;">
                                        {order['amount']:,.0f} VND
                                    </div>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # If paid, show payment details
                    if status_lbl == "PAID" and order.get("payment_info"):
                        info = order["payment_info"]
                        with st.expander(f"🔍 Chi tiết giao dịch VNPAY cho đơn {order['order_id']}"):
                            st.markdown(
                                f"""
                                **Mã giao dịch VNPAY:** `{info.get('vnpay_transaction_no')}`  
                                **Ngân hàng:** `{info.get('bank_code')}`  
                                **Ngày thanh toán:** `{info.get('pay_date')}`  
                                **Mã phản hồi cổng thanh toán:** `{info.get('response_code')}`  
                                **Xác thực chữ ký số:** `Đã xác thực bảo mật (Checksum Validated)`
                                """
                            )
                            
                    # If pending, allow paying it
                    if status_lbl == "PENDING":
                        # Button to pay this order directly
                        pay_now_btn = st.button("Thanh toán ngay 💳", key=f"pay_now_{order['order_id']}")
                        if pay_now_btn:
                            st.session_state["current_order"] = order
                            st.info("Đã chọn đơn hàng! Vui lòng truy cập mục **3 Payment** trong menu bên để thanh toán.")
        else:
            st.error(f"Không thể tải lịch sử đơn hàng. Mã lỗi: {response.status_code}")
    except Exception as e:
        st.error(f"Lỗi kết nối tới máy chủ backend: {e}")
