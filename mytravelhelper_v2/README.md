# MyTravelHelper — Trợ Lý Du Lịch Thông Minh Đa Ngôn Ngữ (v2.0 Multilingual)

Ứng dụng **MyTravelHelper v2.0** là phiên bản nâng cấp hỗ trợ đa ngôn ngữ **Tiếng Việt 🇻🇳 & Tiếng Anh 🇺🇸**, sử dụng **Streamlit** cho giao diện người dùng và các mô hình xử lý ngôn ngữ tiên tiến qua **Hugging Face Inference Providers**, kết hợp lớp dịch thuật trung gian **Google Translate API** theo chiến lược **Translate-then-Process**.

Dự án được tối ưu hóa để tự động nhận diện ngôn ngữ đầu vào, phân tích cảm xúc khía cạnh, phân loại ý định, trích xuất thực thể (NER bảo toàn tên địa danh Việt Nam), và gom cụm chủ đề song ngữ.

---

## 🚀 Tính năng nâng cấp ở v2.0

### 1. Hỗ trợ Đa Ngôn Ngữ (Vietnamese & English)
- **Engine dịch thuật:** Tích hợp `googletrans` và `deep-translator` (GoogleTranslator) làm cơ chế dự phòng tự động (không cần API key cho demo). Hỗ trợ cấu hình Google Cloud Translation API trong môi trường production.
- **Phát hiện ngôn ngữ:** Tự động phát hiện ngôn ngữ đầu vào qua thư viện `langdetect`.

### 2. Phân tích cảm xúc theo khía cạnh (ABSA) song ngữ
- **Mô hình:** `yangheng/deberta-v3-base-absa-v1.1`
- **Mô tả:** Nhận review tiếng Việt, dịch sang tiếng Anh để chạy mô hình ABSA chất lượng cao, sau đó ánh xạ ngược tên khía cạnh và cảm xúc hiển thị dưới dạng song ngữ (ví dụ: *phòng ốc (room)* -> *TÍCH CỰC (POSITIVE)*).

### 3. Phân loại ý định & Trích xuất thực thể (Intent & Hybrid NER)
- **Mô hình:** `facebook/bart-large-mnli` (Zero-shot) và `dslim/bert-base-NER` (NER).
- **Mô tả:** Áp dụng thuật toán **Name Preservation** giúp giữ nguyên định dạng tên riêng địa danh Việt Nam có dấu (như "Đà Nẵng", "Phú Quốc") và các thông tin số tiền (như "10 triệu") từ câu gốc tiếng Việt sau khi chạy mô hình NER tiếng Anh.

### 4. Gom cụm chủ đề review tự động (Topic Modeling)
- **Mô hình:** `BERTopic` / KMeans fallback + Zero-shot labelling.
- **Mô tả:** Cho phép gom cụm hàng loạt các đánh giá bằng tiếng Việt bằng cách dịch tự động dạng batch sang tiếng Anh, gom cụm và dịch ngược các từ đại diện cùng tên chủ đề sang tiếng Việt.

### 5. Công cụ dịch thuật tự do (Free Translation Tool)
- **Mô tả:** Bổ sung Tab 4 chuyên dụng cho phép dịch tự do 2 chiều English ↔ Vietnamese với nút đảo chiều ngôn ngữ `⇄` thông minh.

---

## 📂 Cấu trúc dự án v2.0

Dự án được tổ chức theo kiến trúc modular hóa:

```text
MyTravelHelper/
├── app.py                            # Giao diện chính Streamlit App v2.0
├── requirements.txt                  # Thư viện dependencies cập nhật v2.0
├── .env.example                      # File mẫu cấu hình biến môi trường
├── README.md                         # Tài liệu hướng dẫn sử dụng
├── MyTravelHelper_v2_Multilingual.ipynb # Notebook quy trình v2.0 (đã chạy lưu output)
├── test_v2.py                        # Kịch bản kiểm thử tự động toàn bộ module v2.0
├── config/
│   ├── vi_labels.json                # Bảng ánh xạ dịch nhãn từ EN -> VI
│   └── travel_aspects_vi.json        # Từ khóa fallback tiếng Việt cho các khía cạnh
├── data/
│   ├── sample_reviews.json           # Review mẫu tiếng Anh
│   └── sample_reviews_vi.json        # 16 review mẫu tiếng Việt đa khía cạnh
├── modules/
│   ├── __init__.py
│   ├── sentiment.py                  # Module ABSA v2.0 (tích hợp translation wrapper)
│   ├── intent_ner.py                 # Module Intent & NER v2.0 (tích hợp translation & alignment)
│   ├── topic.py                      # Module BERTopic v2.0 (tích hợp batch translation & keyword translate)
│   └── translation.py                # Lớp dịch thuật TranslationService v2.0
├── utils/
│   ├── __init__.py
│   ├── preprocessing.py              # Chuẩn hóa văn bản Unicode NFC tiếng Việt
│   ├── language_detect.py            # Nhận dạng ngôn ngữ đầu vào
│   └── display.py                    # Trình diễn UI song ngữ & Plotly
└── unmodified_v1/                    # Thư mục lưu trữ các file v1.0 nguyên bản để đối chiếu
```

---

## 🛠️ Hướng dẫn cài đặt và thiết lập

### 1. Kích hoạt môi trường ảo và cài đặt thư viện
Kích hoạt môi trường ảo của bạn và cài đặt dependencies từ `requirements.txt`:

```bash
# Kích hoạt môi trường ảo (ví dụ với venv có sẵn)
source .venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt
```

### 2. Cấu hình khóa Hugging Face API
Tạo file `.env` từ `.env.example` và thiết lập token Hugging Face để kết nối các mô hình API trực tuyến:
```env
HF_TOKEN=hf_your_actual_token_here
```

---

## 🏃 Chạy thử nghiệm và Khởi chạy ứng dụng

### 1. Chạy kiểm thử tự động toàn bộ các chức năng v2.0
Trước khi khởi chạy giao diện, bạn có thể chạy kịch bản test để kiểm tra tính đúng đắn của toàn bộ luồng xử lý đa ngôn ngữ:

```bash
python3 test_v2.py
```
Nếu tất cả 5 bộ test thành công, màn hình sẽ hiển thị thông báo `ALL MULTILINGUAL V2 TESTS PASSED SUCCESSFULLY!`.

### 2. Khởi chạy giao diện Streamlit App v2.0
Chạy lệnh sau để bật giao diện ứng dụng:

```bash
streamlit run app.py
```
Mở trình duyệt tại địa chỉ `http://localhost:8501`.

### 3. Xem Jupyter Notebook v2.0
Mở file `MyTravelHelper_v2_Multilingual.ipynb` bằng editor hỗ trợ Jupyter để xem báo cáo so sánh chi tiết, sơ đồ Mermaid pipeline nâng cấp và kết quả kiểm thử thực tế của phiên bản v2.0.
