import streamlit as st
import httpx
from utils.display import inject_premium_styles

# Page Config
st.set_page_config(
    page_title="MyTravelHelper — Đăng nhập / Đăng ký",
    page_icon="🔑",
    layout="wide"
)

# Apply premium styles
inject_premium_styles()

BACKEND_URL = "http://localhost:8000"

st.markdown(
    """
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1 style='color:#000000; margin-bottom: 5px; font-family: "Nunito", sans-serif;'>🔐 Xác Thực Tài Khoản</h1>
        <p style='color:#737373; font-size:1rem;'>Đăng nhập hoặc đăng ký tài khoản để bắt đầu đặt dịch vụ và thanh toán qua VNPAY</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Render main panel
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Sidebar status display
    if "user_info" in st.session_state and st.session_state["user_info"]:
        user = st.session_state["user_info"]
        st.success(f"🎉 Bạn đang đăng nhập với tài khoản: **{user.get('email')}**")
        st.info(f"Tên hiển thị: **{user.get('display_name')}**")
        st.markdown(f"User ID: `{user.get('uid')}`")
        
        if st.button("Đăng xuất", type="primary", use_container_width=True):
            st.session_state["user_info"] = None
            st.session_state["user_token"] = None
            st.success("Đăng xuất thành công!")
            st.rerun()
    else:
        tab_login, tab_register = st.tabs(["🔑 Đăng Nhập", "📝 Đăng Ký Tài Khoản"])
        
        with tab_login:
            st.markdown("### Đăng Nhập")
            with st.form("form_login"):
                email = st.text_input("Địa chỉ Email", placeholder="email@example.com")
                password = st.text_input("Mật khẩu", type="password", placeholder="••••••••")
                submit = st.form_submit_button("Đăng Nhập", use_container_width=True)
                
                if submit:
                    if not email.strip() or not password.strip():
                        st.error("Vui lòng nhập đầy đủ email và mật khẩu.")
                    else:
                        with st.spinner("Đang xác thực..."):
                            try:
                                payload = {"email": email, "password": password}
                                response = httpx.post(f"{BACKEND_URL}/api/auth/login", json=payload, timeout=10.0)
                                
                                if response.status_code == 200:
                                    data = response.json()
                                    st.session_state["user_token"] = data["id_token"]
                                    st.session_state["user_info"] = {
                                        "uid": data["uid"],
                                        "email": data["email"],
                                        "display_name": data["display_name"]
                                    }
                                    st.success("Đăng nhập thành công!")
                                    st.rerun()
                                else:
                                    detail = response.json().get("detail", "Đăng nhập thất bại")
                                    st.error(f"Lỗi: {detail}")
                            except Exception as e:
                                st.error(f"Không thể kết nối tới máy chủ backend: {e}")
                                
        with tab_register:
            st.markdown("### Đăng Ký")
            with st.form("form_register"):
                reg_name = st.text_input("Tên hiển thị", placeholder="Nguyen Van A")
                reg_email = st.text_input("Địa chỉ Email", placeholder="email@example.com")
                reg_password = st.text_input("Mật khẩu (tối thiểu 6 ký tự)", type="password", placeholder="••••••••")
                reg_submit = st.form_submit_button("Đăng Ký", use_container_width=True)
                
                if reg_submit:
                    if not reg_name.strip() or not reg_email.strip() or not reg_password.strip():
                        st.error("Vui lòng điền đầy đủ các thông tin.")
                    elif len(reg_password) < 6:
                        st.error("Mật khẩu phải chứa ít nhất 6 ký tự.")
                    else:
                        with st.spinner("Đang tạo tài khoản..."):
                            try:
                                payload = {
                                    "email": reg_email,
                                    "password": reg_password,
                                    "display_name": reg_name
                                }
                                response = httpx.post(f"{BACKEND_URL}/api/auth/register", json=payload, timeout=10.0)
                                
                                if response.status_code == 200:
                                    st.success("Đăng ký thành công! Bạn có thể chuyển sang tab Đăng nhập.")
                                else:
                                    detail = response.json().get("detail", "Đăng ký thất bại")
                                    st.error(f"Lỗi: {detail}")
                            except Exception as e:
                                st.error(f"Không thể kết nối tới máy chủ backend: {e}")
