import streamlit as st
import httpx
from utils.display import inject_premium_styles

# Page Config
st.set_page_config(
    page_title="MyTravelHelper — Thanh toán đơn hàng",
    page_icon="💳",
    layout="wide"
)

inject_premium_styles()

BACKEND_URL = "http://localhost:8000"

st.markdown(
    """
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1 style='color:#000000; margin-bottom: 5px; font-family: "Nunito", sans-serif;'>💳 Thanh Toán VNPAY</h1>
        <p style='color:#737373; font-size:1rem;'>Thực hiện thanh toán thử nghiệm qua cổng thanh toán VNPAY Sandbox</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Check login status
is_logged_in = "user_token" in st.session_state and st.session_state["user_token"] is not None

if not is_logged_in:
    st.warning("⚠️ Bạn chưa đăng nhập. Vui lòng đăng nhập để thực hiện thanh toán.")
    st.info("Hãy click chọn mục **1 Auth** ở danh sách trang bên trái để đăng nhập.")
    st.stop()

# ----------------- HANDLE CALLBACK / RESULT FROM VNPAY -----------------
# Parse query parameters using modern st.query_params
q_params = st.query_params

if "vnp_ResponseCode" in q_params:
    response_code = q_params["vnp_ResponseCode"]
    order_id = q_params.get("vnp_TxnRef", "Không rõ")
    amount_raw = q_params.get("vnp_Amount")
    bank_code = q_params.get("vnp_BankCode", "NCB")
    txn_no = q_params.get("vnp_TransactionNo", "N/A")
    
    amount = 0.0
    if amount_raw:
        try:
            amount = float(amount_raw) / 100
        except ValueError:
            pass

    st.markdown("### Kết quả thanh toán từ VNPAY")
    
    if response_code == "00":
        st.balloons()
        st.markdown(
            f"""
            <div class="glass-card" style="background: rgba(39, 201, 63, 0.02) !important; border-left: 4px solid #27c93f !important; padding: 25px; margin-bottom: 25px;">
                <h2 style="color: #27c93f !important; margin-top: 0; font-family: 'Nunito', sans-serif;">🎉 Thanh Toán Thành Công!</h2>
                <p style="font-size: 1.1rem; color: #737373;">Đơn hàng của bạn đã được xác thực thanh toán hoàn tất.</p>
                <hr style="border-color: #e5e5e5; margin: 20px 0;">
                <table style="width: 100%; border-collapse: collapse; font-size: 0.95rem;">
                    <tr>
                        <td style="padding: 8px 0; color: #a3a3a3; width: 40%;">Mã đơn hàng:</td>
                        <td style="padding: 8px 0; color: #000000; font-weight: 600;">{order_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #a3a3a3;">Mã giao dịch VNPAY:</td>
                        <td style="padding: 8px 0; color: #000000;">{txn_no}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #a3a3a3;">Số tiền thanh toán:</td>
                        <td style="padding: 8px 0; color: #27c93f; font-weight: 700; font-size: 1.1rem;">{amount:,.0f} VND</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #a3a3a3;">Ngân hàng thanh toán:</td>
                        <td style="padding: 8px 0; color: #000000;">{bank_code}</td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Clear current order from session state since it is paid
        if "current_order" in st.session_state:
            st.session_state["current_order"] = None
    else:
        st.markdown(
            f"""
            <div class="glass-card" style="background: rgba(255, 95, 86, 0.02) !important; border-left: 4px solid #ff5f56 !important; padding: 25px; margin-bottom: 25px;">
                <h2 style="color: #ff5f56 !important; margin-top: 0; font-family: 'Nunito', sans-serif;">❌ Thanh Toán Thất Bại</h2>
                <p style="font-size: 1.1rem; color: #737373;">Đã có lỗi xảy ra hoặc bạn đã hủy giao dịch.</p>
                <hr style="border-color: #e5e5e5; margin: 20px 0;">
                <table style="width: 100%; border-collapse: collapse; font-size: 0.95rem;">
                    <tr>
                        <td style="padding: 8px 0; color: #a3a3a3; width: 40%;">Mã đơn hàng:</td>
                        <td style="padding: 8px 0; color: #000000; font-weight: 600;">{order_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #a3a3a3;">Mã lỗi VNPAY:</td>
                        <td style="padding: 8px 0; color: #ff5f56; font-weight: 600;"><code>{response_code}</code></td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    if st.button("Tiếp tục mua hàng / Xóa thông báo", type="primary", use_container_width=True):
        st.query_params.clear()
        st.rerun()
        
    st.stop()


# ----------------- STANDARD PAYMENT FLOW -----------------
# Check if there is an order in session waiting for payment
current_order = st.session_state.get("current_order")

if not current_order:
    st.info("ℹ️ Không tìm thấy đơn hàng chờ thanh toán. Vui lòng đặt dịch vụ ở trang **2 Services** trước.")
    st.stop()

# Present order details
st.markdown("### Thông tin đơn hàng chờ thanh toán")
st.markdown(
    f"""
    <div class="glass-card" style="margin-bottom: 25px;">
        <table style="width: 100%; border-collapse: collapse; font-size: 1rem;">
            <tr>
                <td style="padding: 10px 0; color: #a3a3a3; width: 40%;">Mã đơn hàng:</td>
                <td style="padding: 10px 0; color: #000000; font-weight: 700;">{current_order['order_id']}</td>
            </tr>
            <tr>
                <td style="padding: 10px 0; color: #a3a3a3;">Loại dịch vụ:</td>
                <td style="padding: 10px 0; color: #000000; font-family: ui-monospace, monospace;">{current_order['service_type'].upper()}</td>
            </tr>
            <tr>
                <td style="padding: 10px 0; color: #a3a3a3;">Tên dịch vụ:</td>
                <td style="padding: 10px 0; color: #000000; font-weight: 600;">{current_order['service_name']}</td>
            </tr>
            <tr>
                <td style="padding: 10px 0; color: #a3a3a3;">Số tiền cần trả:</td>
                <td style="padding: 10px 0; color: #000000; font-weight: 700; font-size: 1.3rem;">{current_order['amount']:,.0f} VND</td>
            </tr>
            <tr>
                <td style="padding: 10px 0; color: #a3a3a3;">Trạng thái đơn hàng:</td>
                <td style="padding: 10px 0; color: #ffbd2e; font-weight: 600;">
                    ⏳ {current_order['status'].upper()}
                </td>
            </tr>
        </table>
    </div>
    """,
    unsafe_allow_html=True
)

# Form to trigger payment url generation
with st.form("form_payment_url"):
    st.markdown("#### Cổng thanh toán VNPAY Sandbox")
    st.write("VNPAY Sandbox cho phép bạn thanh toán thử nghiệm bằng thẻ test mà không mất tiền thật.")
    
    # We can hardcode local dev client ip or let the user input it (VNPAY requires a valid IP format)
    ip_addr = st.text_input("IP Máy khách (được gửi tới VNPAY)", value="127.0.0.1")
    
    submit_pay = st.form_submit_button("Tạo liên kết thanh toán VNPAY 💳", use_container_width=True)
    
    if submit_pay:
        with st.spinner("Đang khởi tạo liên kết thanh toán..."):
            try:
                headers = {"Authorization": f"Bearer {st.session_state['user_token']}"}
                payload = {
                    "order_id": current_order["order_id"],
                    "ip_address": ip_addr
                }
                
                response = httpx.post(
                    f"{BACKEND_URL}/api/payment/create-url",
                    json=payload,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Tạo liên kết thành công! Nhấp vào nút bên dưới để thanh toán:")
                    st.link_button(
                        "Đi tới VNPAY Sandbox để thanh toán 🚀", 
                        data["payment_url"],
                        use_container_width=True,
                        type="primary"
                    )
                else:
                    detail = response.json().get("detail", "Không thể tạo URL thanh toán")
                    st.error(f"Lỗi: {detail}")
            except Exception as e:
                st.error(f"Không thể kết nối tới backend: {e}")
