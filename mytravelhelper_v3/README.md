# MyTravelHelper v3.0 — Tích hợp Thanh toán VNPAY Sandbox & Firebase

Dự án **MyTravelHelper v3.0** được nâng cấp từ phiên bản v2.0 Đa ngôn ngữ, bổ sung thêm hệ thống Backend bằng FastAPI, Cơ chế xác thực người dùng bằng Firebase Authentication, Lưu trữ cơ sở dữ liệu trên Firebase Firestore, và Tích hợp cổng thanh toán thử nghiệm **VNPAY Sandbox**.

---

## 1. Các Tính Năng Nâng Cấp Chính
- **FastAPI Backend (Port 8000):** Tách biệt business logic, quản lý đơn hàng, sinh URL thanh toán VNPAY và xử lý callback/IPN webhook.
- **Firebase Authentication:** Quản lý tài khoản (Đăng ký, Đăng nhập) đồng bộ qua Streamlit và FastAPI.
- **Firebase Firestore Database:** Lưu trữ thông tin người dùng (`/users`), danh sách đơn hàng đặt dịch vụ (`/orders`), và nhật ký giao dịch (`/transactions`).
- **Local Database Fallback (Resilience Mode):** Hệ thống tự động chuyển sang chế độ dữ liệu offline lưu tại file JSON cục bộ (`data/mock_database.json`) khi chưa cấu hình Firebase, giúp chạy demo ngay lập tức mà không bị lỗi crash.
- **VNPAY Sandbox (v2.1.0 API):** Hỗ trợ tạo URL thanh toán và kiểm chứng chữ ký số bảo mật sử dụng thuật toán mã hóa **HMAC-SHA512**.

---

## 2. Cấu Trúc Thư Mục
```
mytravelhelper_v3/
├── VNPAY_Payment_Notebook.ipynb     # Notebook hướng dẫn thuật toán chữ ký
├── streamlit_app.py                  # Giao diện chính (AI Assistant v2.0)
├── main.py                            # FastAPI Backend server
│
├── modules/
│   ├── firebase_auth.py              # Xác thực Firebase Auth
│   ├── firebase_db.py                # Thao tác Firestore & Mock DB
│   ├── vnpay.py                      # Sinh & kiểm tra chữ ký VNPAY
│   ├── models.py                     # Pydantic validation schemas
│   ├── intent_ner.py                 # NLU module (kế thừa v2)
│   ├── sentiment.py                  # Aspect Sentiment (kế thừa v2)
│   ├── topic.py                      # Topic modeling (kế thừa v2)
│   └── translation.py                # Translation module (kế thừa v2)
│
├── pages/
│   ├── 1_Auth.py                     # Giao diện Đăng ký / Đăng nhập
│   ├── 2_Services.py                 # Giao diện Chọn & Đặt dịch vụ du lịch
│   ├── 3_Payment.py                  # Giao diện Nhận link & Xem kết quả VNPAY
│   └── 4_Orders.py                   # Giao diện Xem lịch sử đơn hàng
│
├── config/
│   ├── services.json                 # Metadata các dịch vụ mẫu
│   ├── travel_aspects_vi.json        # Config từ v2
│   ├── vi_labels.json                # Config từ v2
│   └── firebase_credentials.json     # File key Firebase (nếu có, gitignore)
│
├── .env                              # Cấu hình biến môi trường (gitignore)
├── .env.example                      # Template cấu hình
├── requirements.txt                  # Các thư viện phụ thuộc
└── README.md                         # Tài liệu hướng dẫn
```

---

## 3. Hướng Dẫn Cài Đặt & Cấu Hình

### Bước 3.1. Cài đặt thư viện phụ thuộc
Khuyên dùng môi trường ảo Python (Virtual Environment):
```bash
pip install -r requirements.txt
```

### Bước 3.2. Cấu hình file `.env`
Sao chép `.env.example` thành `.env` và cập nhật thông tin:
```bash
cp .env.example .env
```
Các thông số trong `.env`:
- `HF_TOKEN`: Token Hugging Face để chạy các tác vụ AI NLU.
- `FIREBASE_WEB_API_KEY`: API Key lấy từ Project Settings trên Firebase Console để hỗ trợ Client Đăng nhập.
- `FIREBASE_PROJECT_ID`: ID dự án Firebase của bạn.
- `VNPAY_TMN_CODE`: Mã Merchant TMN Code nhận được từ VNPAY.
- `VNPAY_HASH_SECRET`: Chuỗi khóa bí mật nhận được từ VNPAY để tạo chữ ký HMAC-SHA512.

### Bước 3.3. Thiết lập Firebase Service Account
1. Đi tới **Firebase Console** -> Cấu hình dự án (Project Settings) -> **Service Accounts**.
2. Nhấn nút **Generate new private key** để tải về file JSON.
3. Đổi tên file tải về thành `firebase_credentials.json` và di chuyển vào thư mục `mytravelhelper_v3/config/`.

---

## 4. Chạy Ứng Dụng

### Bước 4.1. Khởi chạy FastAPI Backend
Mở một terminal mới tại thư mục `mytravelhelper_v3`:
```bash
uvicorn main:app --port 8000 --reload
```
API docs sẽ khả dụng tại: `http://localhost:8000/docs`.

### Bước 4.2. Cài đặt và cấu hình Ngrok (Bắt buộc cho VNPAY IPN)

VNPAY IPN hoạt động theo cơ chế **server-to-server**: sau khi người dùng thanh toán, server VNPAY sẽ gọi ngược về backend của bạn để xác nhận giao dịch. Vì VNPAY **không thể gọi tới `localhost`**, bạn cần dùng Ngrok để tạo một đường hầm (tunnel) public ra internet.

#### Bước 4.2.1. Cài đặt Ngrok qua Homebrew
```bash
brew install ngrok/ngrok/ngrok
```

#### Bước 4.2.2. Đăng ký tài khoản Ngrok (miễn phí)
1. Truy cập **https://dashboard.ngrok.com/signup** và đăng ký tài khoản.
2. Sau khi đăng nhập, vào trang **https://dashboard.ngrok.com/get-started/your-authtoken**.
3. Sao chép **Authtoken** của bạn.

#### Bước 4.2.3. Cấu hình Authtoken (chỉ cần chạy 1 lần duy nhất)
```bash
ngrok config add-authtoken <PASTE_AUTHTOKEN_CỦA_BẠN>
```
Ví dụ:
```bash
ngrok config add-authtoken 2abc123xyz456_7defABCtoken
```

#### Bước 4.2.4. Khởi chạy Ngrok Tunnel trên port 8000
Mở một **terminal riêng** và chạy:
```bash
ngrok http 8000
```
Ngrok sẽ hiển thị giao diện như sau:
```
Session Status    online
Forwarding        https://abcd-12-34.ngrok-free.app -> http://localhost:8000
```
Sao chép URL HTTPS được sinh ra (ví dụ: `https://abcd-12-34.ngrok-free.app`).

#### Bước 4.2.5. Cập nhật file `.env` với URL Ngrok
Mở file `.env` tại thư mục `mytravelhelper_v3` và thay đổi 2 dòng sau:
```env
VNPAY_RETURN_URL=https://abcd-12-34.ngrok-free.app/api/payment/return
VNPAY_IPN_URL=https://abcd-12-34.ngrok-free.app/api/payment/ipn
```
*(Thay `abcd-12-34.ngrok-free.app` bằng domain thực tế mà Ngrok cấp cho bạn)*

> **⚠️ Lưu ý quan trọng:**
> - Mỗi lần restart Ngrok, domain sẽ **thay đổi** (trừ khi dùng gói trả phí với static domain). Bạn cần cập nhật lại `.env` và restart FastAPI server mỗi lần.
> - Giữ cửa sổ terminal Ngrok **luôn mở** trong suốt quá trình kiểm thử. Nếu đóng terminal, tunnel sẽ ngắt.
> - Sau khi cập nhật `.env`, **restart lại FastAPI server** để nạp cấu hình mới.

#### Bước 4.2.6. (Tùy chọn) Cập nhật IPN URL trên trang quản trị VNPAY Sandbox
Nếu bạn muốn VNPAY gọi IPN webhook trực tiếp:
1. Đăng nhập vào **https://sandbox.vnpayment.vn/merchantv2/**.
2. Vào **Cấu hình kỹ thuật** → cập nhật **IPN URL** thành: `https://abcd-12-34.ngrok-free.app/api/payment/ipn`.

### Bước 4.3. Khởi chạy Streamlit Frontend
Mở một terminal mới tại thư mục `mytravelhelper_v3`:
```bash
NUMBA_NUM_THREADS=1 ./venv/bin/streamlit run streamlit_app.py --server.fileWatcherType none
```
Trình duyệt sẽ tự động mở giao diện tại địa chỉ: `http://localhost:8501`.

### Bước 4.4. Khởi chạy Vite React Frontend
Mở một terminal mới tại thư mục `mytravelhelper_v3/frontend`:
```bash
npm install
npm run dev
```
Giao diện React hiện đại sẽ chạy tại địa chỉ: `http://localhost:5173`.

---

## 5. Lưu ý về Nghiệm thu và Kiểm thử IPN
VNPAY IPN hoạt động theo cơ chế server-to-server. Nếu VNPAY không thể gọi trực tiếp tới cổng backend của bạn (do bạn chạy localhost hoặc chưa cấu hình Ngrok):
- **Cơ chế Fallback (Tự động):** Khi người dùng thanh toán xong và được VNPAY redirect về `api/payment/return` (Client-side), backend sẽ tự động xác minh chữ ký và cập nhật trạng thái đơn hàng sang `paid`/`failed` trực tiếp vào database.
- **Mock IPN request:** Bạn cũng có thể giả lập request IPN bằng cách gửi một POST request tới `http://localhost:8000/api/payment/ipn` kèm theo các tham số nhận được trong URL Redirect để kiểm tra tính năng độc lập của IPN.

---

## 6. Thông Tin Thẻ Kiểm Thử VNPAY Sandbox
Sử dụng thông tin thẻ sau để thực hiện giao dịch giả lập trên cổng VNPAY NCB:

| Thông số | Giá trị |
|---|---|
| Ngân hàng | **NCB** |
| Số thẻ | **9704198526191432198** |
| Tên chủ thẻ | **NGUYEN VAN A** |
| Ngày phát hành | **07/15** |
| Mật khẩu OTP | **123456** |

---

## 7. Tổng Hợp Thứ Tự Khởi Chạy (4 Terminal)

Bạn cần mở **4 cửa sổ terminal riêng biệt** và chạy theo đúng thứ tự:

| Terminal | Lệnh | Mục đích |
|---|---|---|
| **Terminal 1** | `ngrok http 8000` | Tạo tunnel public cho VNPAY gọi IPN |
| **Terminal 2** | `./venv/bin/uvicorn main:app --port 8000 --reload` | Khởi chạy FastAPI Backend |
| **Terminal 3** | `cd frontend && npm run dev` | Khởi chạy React Frontend (port 5173) |
| **Terminal 4** *(tùy chọn)* | `NUMBA_NUM_THREADS=1 ./venv/bin/streamlit run streamlit_app.py --server.fileWatcherType none` | Khởi chạy Streamlit Frontend (port 8501) |

> **⚠️ Quan trọng:** Sau khi chạy Ngrok ở Terminal 1, hãy sao chép URL HTTPS (ví dụ: `https://bunt-ended-carpool.ngrok-free.dev`) và cập nhật vào file `.env` **trước khi** khởi chạy FastAPI ở Terminal 2:
> ```env
> VNPAY_RETURN_URL=https://bunt-ended-carpool.ngrok-free.dev/api/payment/return
> VNPAY_IPN_URL=https://bunt-ended-carpool.ngrok-free.dev/api/payment/ipn
> FRONTEND_URL=http://localhost:5173
> ```

---

## 8. Hướng Dẫn Kiểm Thử Luồng Thanh Toán End-to-End

### Bước 8.1. Đăng ký / Đăng nhập tài khoản
1. Mở trình duyệt tại `http://localhost:5173` (React) hoặc `http://localhost:8501` (Streamlit).
2. Nhấn vào biểu tượng menu góc trên bên phải → **Đăng nhập / Đăng ký**.
3. Tạo tài khoản mới hoặc đăng nhập bằng tài khoản đã có.

### Bước 8.2. Chọn dịch vụ và đặt phòng
1. Chọn một điểm đến trên trang chủ (ví dụ: *Resort bãi biển Phú Quốc*).
2. Nhấn **"Khám phá ngay"** → Xem chi tiết → Nhấn **"Đặt phòng ngay"**.
3. Hệ thống sẽ tự động tạo đơn hàng và chuyển hướng bạn tới cổng thanh toán VNPAY Sandbox.

### Bước 8.3. Thanh toán trên VNPAY Sandbox
1. Chọn ngân hàng **NCB**.
2. Nhập thông tin thẻ kiểm thử (xem Mục 6 ở trên).
3. Nhấn **Tiếp tục** → Nhập OTP `123456` → Xác nhận thanh toán.

### Bước 8.4. Xác nhận kết quả
1. VNPAY sẽ redirect trở về ứng dụng React (`http://localhost:5173`).
2. Một **hóa đơn xác nhận** sẽ hiện lên hiển thị: mã đơn hàng, số tiền, ngân hàng, mã giao dịch VNPAY.
3. Trạng thái đơn hàng trong database sẽ được cập nhật thành `paid`.

