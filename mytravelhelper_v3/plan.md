# MyTravelHelper — Kế hoạch Tích hợp Thanh toán VNPAY Sandbox

> **Phiên bản:** 3.0.0 (nâng cấp từ v2.0 — Đa ngôn ngữ)  
> **Stack:** Python · Streamlit · FastAPI · Firebase · VNPAY Sandbox  
> **Ngày tạo:** 2026-06-07  
> **Trạng thái:** Planning

---

## Mục lục

1. [Tổng quan & Mục tiêu](#1-tổng-quan--mục-tiêu)
2. [Phân tích yêu cầu](#2-phân-tích-yêu-cầu)
3. [Kiến trúc tổng quát](#3-kiến-trúc-tổng-quát)
4. [Thiết lập VNPAY Sandbox](#4-thiết-lập-vnpay-sandbox)
5. [Thiết lập Firebase](#5-thiết-lập-firebase)
6. [Cấu trúc dữ liệu Firebase](#6-cấu-trúc-dữ-liệu-firebase)
7. [Luồng nghiệp vụ chi tiết](#7-luồng-nghiệp-vụ-chi-tiết)
8. [Cấu trúc project](#8-cấu-trúc-project)
9. [Kế hoạch triển khai](#9-kế-hoạch-triển-khai)
10. [Kiểm thử](#10-kiểm-thử)
11. [Lộ trình nâng cấp](#11-lộ-trình-nâng-cấp)
12. [Rủi ro & Dự phòng](#12-rủi-ro--dự-phòng)
13. [Checklist nộp bài](#13-checklist-nộp-bài)

---

## 1. Tổng quan & Mục tiêu

### 1.1 Bối cảnh nâng cấp

| Phiên bản | Tính năng chính |
|---|---|
| v1.0 (Tuần 09) | NLP pipeline: ABSA · Intent · NER · Topic Detection (EN) |
| v2.0 (Tuần 10) | Đa ngôn ngữ VI/EN · Google Translate API · Tab dịch thuật |
| **v3.0 (Hiện tại)** | **Thanh toán VNPAY Sandbox · Firebase Auth · FastAPI backend** |

### 1.2 Mục tiêu cụ thể

- Tích hợp **VNPAY Sandbox** để xử lý thanh toán thử nghiệm
- Xây dựng **FastAPI backend** xử lý business logic tách biệt khỏi Streamlit
- Dùng **Firebase Authentication** cho đăng ký/đăng nhập người dùng
- Dùng **Firebase Firestore** lưu trữ đơn hàng và trạng thái thanh toán
- Xử lý đầy đủ 3 luồng: tạo URL thanh toán → callback return URL → IPN webhook

---

## 2. Phân tích yêu cầu

### 2.1 Functional Requirements

| ID | Yêu cầu | Điểm | Mức độ |
|---|---|---|---|
| FR-01 | Đăng ký tài khoản bằng email/password (Firebase Auth) | 2đ | Must Have |
| FR-02 | Đăng nhập và truy cập trang thanh toán (session management) | 2đ | Must Have |
| FR-03 | Tạo đơn hàng và generate VNPAY payment URL | - | Must Have |
| FR-04 | Redirect người dùng đến VNPAY Sandbox để thanh toán | 2đ | Must Have |
| FR-05 | Nhận return URL callback và hiển thị kết quả cho user | 2đ | Must Have |
| FR-06 | Backend nhận IPN từ VNPAY, verify HMAC-SHA512 | 2đ | Must Have |
| FR-07 | Cập nhật trạng thái đơn hàng vào Firebase Firestore | 2đ | Must Have |
| FR-08 | Hiển thị lịch sử đơn hàng của user | - | Should Have |
| FR-09 | Admin dashboard xem tất cả transactions | - | Nice to Have |

### 2.2 Non-Functional Requirements

| Thuộc tính | Yêu cầu |
|---|---|
| Security | HMAC-SHA512 signature verification cho mọi VNPAY response |
| Idempotency | IPN handler không xử lý duplicate notifications |
| Timeout | Payment URL hết hạn sau 15 phút (configurable) |
| Logging | Log đầy đủ mọi VNPAY request/response để debug |

### 2.3 VNPAY Sandbox — Thông tin kỹ thuật

| Thông số | Giá trị |
|---|---|
| Môi trường | sandbox.vnpayment.vn |
| API Version | 2.1.0 |
| Hash Algorithm | HMAC-SHA512 |
| Đơn vị tiền tệ | VND (× 100 khi gửi lên VNPAY) |
| Thẻ test | 9704198526191432198 / NGUYEN VAN A / 07/15 / OTP: 123456 |

---

## 3. Kiến trúc tổng quát

### 3.1 Component Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         NGƯỜI DÙNG (Browser)                       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTPS
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND (Port 8501)                   │
│  Page: Login/Register │ Home │ Booking │ Payment │ Order History    │
│  Session State: user_token · cart · current_order                   │
└────────────────┬──────────────────────────────┬─────────────────────┘
                 │ REST API calls                │ Firebase SDK (Auth)
                 ▼                               ▼
┌───────────────────────────────┐   ┌──────────────────────────────┐
│  FASTAPI BACKEND (Port 8000)  │   │  FIREBASE AUTHENTICATION     │
│                               │   │  - Email/Password Auth       │
│  POST /api/orders/create      │   │  - ID Token verification     │
│  GET  /api/orders/{id}        │   │  - User management           │
│  POST /api/payment/create-url │   └──────────────────────────────┘
│  GET  /api/payment/return     │
│  POST /api/payment/ipn        │──────────────────────────────────┐
│  GET  /api/orders/history     │                                  │
└───────────────┬───────────────┘                                  │
                │                                                  │
    ┌───────────┴──────────┐                                       │
    │                      │                                       │
    ▼                      ▼                                       ▼
┌──────────────┐  ┌─────────────────────┐            ┌────────────────────┐
│  VNPAY       │  │  FIREBASE FIRESTORE │            │  FIREBASE FIRESTORE│
│  SANDBOX     │  │                     │            │  (IPN updates)     │
│              │  │  Collections:       │            │                    │
│  Payment     │  │  - users/           │            │  orders/{id}       │
│  Gateway     │  │  - orders/          │            │  .status = PAID    │
│              │  │  - transactions/    │            │  .ipn_received = T │
└──────┬───────┘  └─────────────────────┘            └────────────────────┘
       │
       │ Return URL (GET)
       │ IPN URL (POST) — server-to-server
       └──────────────────────► FastAPI Backend
```

### 3.2 Payment Flow Sequence

```
User        Streamlit     FastAPI      VNPAY         Firebase
 │               │            │           │               │
 │──[Chọn dịch vụ]──►         │           │               │
 │               │──[POST /orders/create]►│               │
 │               │            │──────────────────────────►│ create order
 │               │            │◄──────────────────────────│ order_id
 │               │◄──[order_id]           │               │
 │               │──[POST /payment/create-url]►           │
 │               │            │──[Build URL + HMAC]       │
 │               │◄──[payment_url]        │               │
 │──◄[Redirect to VNPAY]──    │           │               │
 │                            │           │               │
 │──────────────────────────────────────►│ Nhập thẻ test │
 │◄──────────────────────────────────────│ Thanh toán    │
 │                            │           │               │
 │               │            │◄──[IPN POST — server2server]         │
 │               │            │──[Verify HMAC-SHA512]     │          │
 │               │            │──────────────────────────────────────►│ update status
 │               │            │──[Return "00"]──►│        │           │
 │               │            │                  │        │           │
 │──◄[Return URL redirect]────│◄────────────────│        │           │
 │               │──[Verify + show result]       │        │           │
 │──◄[Hiển thị kết quả thanh toán]              │        │           │
```

---

## 4. Thiết lập VNPAY Sandbox

### 4.1 Đăng ký tài khoản

```
1. Truy cập: https://sandbox.vnpayment.vn/devreg/
2. Điền thông tin: tên website, domain, email
3. Nhận email xác nhận → lấy TMN Code và Hash Secret
4. Lưu vào .env:
   VNPAY_TMN_CODE=XXXXXXXX
   VNPAY_HASH_SECRET=your_hash_secret_here
   VNPAY_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
   VNPAY_RETURN_URL=http://localhost:8000/api/payment/return
   VNPAY_IPN_URL=http://localhost:8000/api/payment/ipn
```

### 4.2 Cấu hình IPN URL (Quan trọng)

Vì IPN là server-to-server, VNPAY cần gọi được vào server của bạn:
- **Local dev:** Dùng `ngrok` để expose localhost
  ```bash
  ngrok http 8000
  # Copy URL: https://xxxx.ngrok-free.app
  # Cập nhật VNPAY_IPN_URL=https://xxxx.ngrok-free.app/api/payment/ipn
  ```
- **Production:** Dùng domain thật với HTTPS

### 4.3 Thẻ test VNPAY Sandbox

| Thông tin | Giá trị |
|---|---|
| Số thẻ | 9704198526191432198 |
| Tên chủ thẻ | NGUYEN VAN A |
| Ngày phát hành | 07/15 |
| OTP | 123456 |
| Ngân hàng | NCB |

---

## 5. Thiết lập Firebase

### 5.1 Tạo Firebase Project

```
1. Truy cập https://console.firebase.google.com
2. Tạo project: "mytravelhelper-payment"
3. Enable Authentication → Email/Password
4. Enable Firestore Database → Start in test mode
5. Project Settings → Service Accounts → Generate private key
6. Lưu file JSON → firebase_credentials.json
7. Thêm vào .env:
   FIREBASE_WEB_API_KEY=AIza...
   FIREBASE_PROJECT_ID=mytravelhelper-payment
```

---

## 6. Cấu trúc dữ liệu Firebase

### 6.1 Firestore Collections

```
firestore/
├── users/{uid}/
│   ├── email: string
│   ├── display_name: string
│   ├── created_at: timestamp
│   └── total_spent: number
│
├── orders/{order_id}/
│   ├── uid: string (Firebase Auth UID)
│   ├── service_type: string  # "hotel_booking" | "tour" | "flight"
│   ├── service_name: string
│   ├── amount: number        # VND
│   ├── status: string        # "pending" | "paid" | "failed" | "cancelled"
│   ├── created_at: timestamp
│   ├── updated_at: timestamp
│   ├── vnpay_txn_ref: string  # = order_id (unique per transaction)
│   └── payment_info/          # Sub-collection sau khi thanh toán
│       ├── vnpay_transaction_no: string
│       ├── bank_code: string
│       ├── pay_date: string
│       ├── response_code: string
│       └── secure_hash_verified: boolean
│
└── transactions/{txn_id}/
    ├── order_id: string
    ├── uid: string
    ├── amount: number
    ├── type: string    # "ipn" | "return"
    ├── raw_data: map   # Toàn bộ VNPAY response
    ├── verified: boolean
    └── created_at: timestamp
```

---

## 7. Luồng nghiệp vụ chi tiết

### 7.1 Luồng Đăng ký & Đăng nhập

```
[Streamlit Page: /auth]
    │
    ├── Tab "Đăng ký"
    │     ├── Input: email, password, display_name
    │     ├── Validate: email format, password >= 8 chars
    │     ├── Firebase Auth: createUserWithEmailAndPassword()
    │     ├── Firestore: tạo document users/{uid}
    │     └── Lưu session: st.session_state.user_token
    │
    └── Tab "Đăng nhập"
          ├── Input: email, password
          ├── Firebase Auth REST API: signInWithEmailAndPassword()
          ├── Nhận: idToken, refreshToken, expiresIn
          ├── Verify token: FastAPI /api/auth/verify
          └── Lưu session: st.session_state.user_token, user_info
```

### 7.2 Luồng Tạo đơn hàng & URL thanh toán

```
[Streamlit Page: /payment]
    │
    ├── Kiểm tra session (user đã đăng nhập?)
    │     └── Nếu chưa → redirect /auth
    │
    ├── Hiển thị dịch vụ du lịch (hotel/tour/flight)
    │
    ├── User chọn dịch vụ → [POST /api/orders/create]
    │     ├── Tạo order_id: f"DH{datetime.now():%Y%m%d%H%M%S}{random 4 digits}"
    │     ├── Lưu Firestore: orders/{order_id} với status="pending"
    │     └── Return: order_id, amount
    │
    └── [POST /api/payment/create-url]
          ├── Build vnp_params dict (15+ parameters)
          ├── Sort params alphabetically
          ├── Build query string (URL-encoded)
          ├── HMAC-SHA512(hash_secret, query_string)
          ├── Append vnp_SecureHash
          └── Return: full payment URL
```

### 7.3 Luồng IPN — Server to Server

```
[VNPAY Server] ──POST──► [FastAPI /api/payment/ipn]
    │
    ├── 1. Extract tất cả vnp_* params từ request body
    ├── 2. Tách vnp_SecureHash ra khỏi params
    ├── 3. Sort remaining params alphabetically
    ├── 4. Build query string
    ├── 5. HMAC-SHA512(hash_secret, query_string)
    ├── 6. So sánh với vnp_SecureHash
    │     ├── Không khớp → Return {"RspCode":"97","Message":"Checksum failed"}
    │     └── Khớp → tiếp tục
    ├── 7. Truy vấn Firestore: orders/{vnp_TxnRef}
    │     └── Không tồn tại → Return {"RspCode":"01","Message":"Order not found"}
    ├── 8. Kiểm tra số tiền: vnp_Amount/100 == order.amount
    │     └── Sai → Return {"RspCode":"04","Message":"Invalid amount"}
    ├── 9. Kiểm tra trạng thái (idempotency)
    │     └── Đã xử lý → Return {"RspCode":"02","Message":"Order already confirmed"}
    ├── 10. Cập nhật Firestore:
    │     ├── orders/{id}.status = "paid" (nếu vnp_ResponseCode="00")
    │     ├── orders/{id}.payment_info = {...VNPAY data}
    │     └── transactions/{id} = {full IPN data}
    └── 11. Return {"RspCode":"00","Message":"Confirm Success"}
```

---

## 8. Cấu trúc project

```
MyTravelHelper/
├── 📓 VNPAY_Payment_Notebook.ipynb     ← Notebook trình bày
├── 🖥️  streamlit_app.py                ← Streamlit frontend
├── ⚡  main.py                          ← FastAPI backend
│
├── 📁 modules/
│   ├── vnpay.py                        ← VNPAY helper (URL, verify)
│   ├── firebase_auth.py                ← Firebase Auth wrapper
│   ├── firebase_db.py                  ← Firestore CRUD
│   └── models.py                       ← Pydantic models
│
├── 📁 pages/  (Streamlit multipage)
│   ├── 1_Auth.py                       ← Đăng ký / Đăng nhập
│   ├── 2_Services.py                   ← Chọn dịch vụ du lịch
│   ├── 3_Payment.py                    ← Thanh toán & kết quả
│   └── 4_Orders.py                     ← Lịch sử đơn hàng
│
├── 📁 config/
│   ├── services.json                   ← Danh sách dịch vụ du lịch
│   └── firebase_credentials.json      ← Firebase service account (gitignore)
│
├── .env                                ← Biến môi trường (gitignore)
├── .env.example                        ← Template .env
├── .gitignore
└── requirements.txt
```

---

## 9. Kế hoạch triển khai

### Sprint 1 — Foundation (3h)

| Task | Mô tả | Thời gian |
|---|---|---|
| T1.1 | Đăng ký VNPAY Sandbox, lấy TMN Code + Hash Secret | 30 phút |
| T1.2 | Tạo Firebase project, enable Auth + Firestore | 30 phút |
| T1.3 | Setup project structure, .env, requirements.txt | 20 phút |
| T1.4 | Viết modules/vnpay.py (build URL + verify) | 60 phút |
| T1.5 | Viết modules/firebase_auth.py + firebase_db.py | 40 phút |

### Sprint 2 — Core Backend (3h)

| Task | Mô tả | Thời gian |
|---|---|---|
| T2.1 | FastAPI: POST /api/orders/create | 30 phút |
| T2.2 | FastAPI: POST /api/payment/create-url | 45 phút |
| T2.3 | FastAPI: GET /api/payment/return (callback) | 45 phút |
| T2.4 | FastAPI: POST /api/payment/ipn (webhook) | 60 phút |

### Sprint 3 — Streamlit Frontend (3h)

| Task | Mô tả | Thời gian |
|---|---|---|
| T3.1 | pages/1_Auth.py — Đăng ký + Đăng nhập | 60 phút |
| T3.2 | pages/2_Services.py — Chọn dịch vụ | 30 phút |
| T3.3 | pages/3_Payment.py — Thanh toán + Kết quả | 60 phút |
| T3.4 | pages/4_Orders.py — Lịch sử đơn hàng | 30 phút |

### Sprint 4 — Testing & Notebook (2h)

| Task | Mô tả | Thời gian |
|---|---|---|
| T4.1 | Test end-to-end với thẻ VNPAY Sandbox | 45 phút |
| T4.2 | Test IPN với ngrok | 30 phút |
| T4.3 | Hoàn thiện notebook (commentary + diagrams) | 45 phút |

---

## 10. Kiểm thử

### 10.1 Test Cases

| ID | Test Case | Expected | Pass/Fail |
|---|---|---|---|
| TC-01 | Đăng ký email mới | Tạo user Firebase thành công | ⬜ |
| TC-02 | Đăng nhập sai password | Hiển thị lỗi thân thiện | ⬜ |
| TC-03 | Tạo đơn hàng 500,000 VND | Order xuất hiện trong Firestore status=pending | ⬜ |
| TC-04 | Generate payment URL | URL hợp lệ, có vnp_SecureHash | ⬜ |
| TC-05 | Thanh toán thành công (thẻ test) | Return URL vnp_ResponseCode=00 | ⬜ |
| TC-06 | Thanh toán thất bại (hủy) | Return URL vnp_ResponseCode≠00 | ⬜ |
| TC-07 | IPN nhận được sau thanh toán | Firestore status → paid | ⬜ |
| TC-08 | IPN giả mạo (sai HMAC) | Return RspCode=97, không update DB | ⬜ |
| TC-09 | IPN duplicate | Return RspCode=02, không update lại | ⬜ |
| TC-10 | Xem lịch sử đơn hàng | Hiển thị đúng đơn của user | ⬜ |

---

## 11. Lộ trình nâng cấp

### Phase 1 — v3.1: Production Ready (2–3 tuần)

- [ ] Deploy FastAPI lên **Railway / Render** (free tier)
- [ ] Deploy Streamlit lên **Streamlit Cloud**
- [ ] Cấu hình HTTPS domain thật cho VNPAY IPN
- [ ] Chuyển từ Sandbox → VNPAY Production
- [ ] Rate limiting trên API endpoints
- [ ] Refresh token flow (Firebase Auth)

### Phase 2 — v3.2: Enhanced Payment (1 tháng)

- [ ] Thêm **ZaloPay** integration
- [ ] Thêm **MoMo** QR payment
- [ ] Payment analytics dashboard (Streamlit)
- [ ] Email confirmation sau khi thanh toán thành công
- [ ] PDF invoice generation (reportlab)

### Phase 3 — v4.0: Full Travel Platform (Dài hạn)

- [ ] Tích hợp booking API thật (Booking.com Affiliate)
- [ ] Kết nối lại NLP pipeline (v1.0) với payment flow
- [ ] Gợi ý dịch vụ dựa trên lịch sử thanh toán
- [ ] Multi-currency (USD/EUR cho khách quốc tế)
- [ ] Loyalty points system (Firebase)

---

## 12. Rủi ro & Dự phòng

| Rủi ro | Khả năng | Phương án dự phòng |
|---|---|---|
| VNPAY Sandbox không ổn định | Thấp | Mock payment response để demo offline |
| ngrok URL thay đổi khi restart | Cao | Dùng ngrok static domain (free) hoặc `localtunnel` |
| Firebase free tier hết quota | Thấp | 50K reads/20K writes/ngày — đủ cho demo |
| HMAC verify fail do encoding | Trung bình | Log raw params, debug từng bước |
| IPN không nhận được | Trung bình | Fallback: verify qua return URL + query VNPAY API |

---

## 13. Checklist nộp bài

### Files bắt buộc

- [ ] `VNPAY_Payment_Notebook.ipynb` — chạy được, có output
- [ ] `streamlit_app.py` + `pages/` — Streamlit app hoàn chỉnh
- [ ] `main.py` — FastAPI backend với đủ 4 endpoints
- [ ] `modules/vnpay.py` — VNPAY helper
- [ ] `modules/firebase_auth.py` + `firebase_db.py`
- [ ] `requirements.txt` — đầy đủ version
- [ ] `.env.example` — template (không có key thật)
- [ ] `README.md` — hướng dẫn setup và chạy

### Kiểm tra chức năng

- [ ] Đăng ký + Đăng nhập hoạt động (Firebase Auth)
- [ ] Tạo đơn hàng → sinh URL VNPAY thành công
- [ ] Thanh toán thành công với thẻ test → hiển thị kết quả
- [ ] IPN endpoint verify HMAC và update Firebase
- [ ] Lịch sử đơn hàng hiển thị đúng

---

*Kế hoạch v3.0 — MyTravelHelper VNPAY Payment Integration*
