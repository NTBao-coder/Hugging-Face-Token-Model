# MyTravelHelper — Trợ Lý Du Lịch Thông Minh (NLP & LLMs)

Ứng dụng **MyTravelHelper** là một hệ thống trợ lý du lịch được xây dựng bằng **Streamlit** cho giao diện người dùng và **Hugging Face Inference Providers** để gọi các mô hình AI/NLP nâng cao. 

Dự án được tối ưu hóa để hoạt động hoàn hảo dưới cả hai chế độ: gọi API đám mây trực tiếp qua Hugging Face Serverless Endpoints và chế độ Heuristic Fallback ngoại tuyến (khi chưa cấu hình token hoặc khi mạng yếu).

---

## 🚀 Tính năng nổi bật

### 1. Phân tích cảm xúc theo khía cạnh (Aspect-Based Sentiment Analysis - ABSA)
- **Model sử dụng:** `yangheng/deberta-v3-base-absa-v1.1`
- **Mô tả:** Phân tích chi tiết cảm xúc của du khách (Tích cực / Tiêu cực / Trung lập) đối với từng khía cạnh cụ thể như: *Dịch vụ, Vị trí, Giá cả, Tiện nghi, Ẩm thực, Vệ sinh*.

### 2. Phân loại ý định & Trích xuất thực thể (Intent & Hybrid NER)
- **Mô hình:** `facebook/bart-large-mnli` (Zero-shot intent classification) kết hợp `dslim/bert-base-NER` (Named Entity Recognition).
- **Mô tả:** Nhận diện ý định người dùng (Hỏi thông tin, Đặt phòng, Phàn nàn, Hỏi thời tiết, v.v.) và trích xuất thông tin hành trình: *Địa danh (Location), Ngày khởi hành (Date), Thời lượng chuyến đi (Duration)* và *Ngân sách dự kiến (Budget)* bằng các biểu thức chính quy (Regex) tối ưu hóa.

### 3. Gom cụm chủ đề review tự động (Topic Modeling)
- **Mô hình:** `BERTopic` với `sentence-transformers` (hoặc thuật toán KMeans + TF-IDF dự phòng).
- **Mô tả:** Nhận đầu vào là hàng loạt các đánh giá của du khách, tự động gom cụm các đánh giá này và dùng mô hình Zero-shot MNLI để dán nhãn đặt tên chủ đề một cách trực quan, sinh động.

---

## 📂 Cấu trúc dự án

Dự án được tổ chức theo kiến trúc modular hóa sạch sẽ và chuyên nghiệp:

```text
MyTravelHelper/
├── app.py                      # Điểm chạy ứng dụng chính (Streamlit UI)
├── requirements.txt            # Danh sách thư viện và dependencies của dự án
├── .env.example                # File mẫu cấu hình biến môi trường
├── README.md                   # Tài liệu hướng dẫn sử dụng
├── notebook.ipynb              # Notebook quy trình, so sánh model và test code (đã chạy lưu output)
├── data/
│   └── sample_reviews.json     # 22 review mẫu đa dạng tiếng Anh & tiếng Việt để chạy demo
├── modules/
│   ├── __init__.py             # Cấu hình nạp biến môi trường và khởi tạo InferenceClient
│   ├── sentiment.py            # Logic xử lý Sentiment và ABSA nâng cao
│   ├── intent_ner.py           # Logic xử lý Intent Classification, NER và LLM Chatbot
│   └── topic.py                # Logic xử lý BERTopic và KMeans fallback
└── utils/
    ├── __init__.py             # Khởi tạo utility package
    ├── preprocessing.py        # Các hàm tiền xử lý text, chuẩn hóa và cắt ngắn text
    └── display.py              # Các helper hiển thị UI Streamlit, CSS, Badges và Plotly Chart
```

---

## 🛠️ Hướng dẫn cài đặt và thiết lập

### 1. Khởi tạo môi trường ảo
Sử dụng `conda`, `micromamba`, hoặc `venv`:

```bash
# Tạo môi trường bằng python 3.11
python3 -m venv .venv
source .venv/bin/activate

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

### 2. Cấu hình khóa Hugging Face API
Để gọi các mô hình AI trực tuyến qua Hugging Face Serverless Inference, hãy làm theo các bước sau:
1. Truy cập [Hugging Face Settings](https://huggingface.co/settings/tokens).
2. Tạo một Token mới (quyền `Read`).
3. Sao chép và tạo file `.env` từ file `.env.example`:

```bash
cp .env.example .env
```

Mở file `.env` và điền token của bạn:
```env
HF_TOKEN=hf_your_actual_token_here
```

*Lưu ý: Nếu không có token, hệ thống vẫn tự động chuyển sang chế độ Heuristics / Local KMeans để demo các luồng bình thường.*

---

## 🏃 Chạy ứng dụng

### Chạy giao diện Streamlit
Giao diện người dùng được tối ưu hóa đẹp mắt và tương tác nhanh chóng:

```bash
streamlit run app.py
```
Sau đó mở trình duyệt tại địa chỉ `http://localhost:8501`.

### Chạy Notebook
Notebook chứa toàn bộ kết quả phân tích định tính, so sánh mô hình và mã chạy thử nghiệm:
Mở `notebook.ipynb` bằng VS Code, Jupyter Lab hoặc Jupyter Notebook để xem chi tiết. Các cell code đã được chạy sẵn và hiển thị kết quả đầy đủ.

---

## 🧪 Kiểm thử mã nguồn

Bạn có thể nhanh chóng kiểm tra cú pháp và khả năng biên dịch của toàn bộ code bằng lệnh sau:

```bash
python3 -m py_compile app.py modules/*.py utils/*.py
```
Lệnh trên sẽ kết thúc thành công mà không trả ra lỗi nào nếu tất cả các module được định vị chính xác.
