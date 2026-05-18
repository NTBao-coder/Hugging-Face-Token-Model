# Project Plan: MyTravelHelper (AI-Powered Tourism Application)

## 1. Mục tiêu và Phân tích yêu cầu (Objectives & Requirements Analysis)
### 1.1. Mục tiêu
Xây dựng một ứng dụng trợ lý du lịch thông minh (MyTravelHelper) với giao diện người dùng trực quan bằng Streamlit. Tích hợp sức mạnh của các mô hình ngôn ngữ lớn (LLMs) và các mô hình xử lý ngôn ngữ tự nhiên (NLP) thông qua Hugging Face Inference Providers.

### 1.2. Phân tích yêu cầu cốt lõi
* **Giao diện (UI):** Tương tác đa chiều qua Streamlit.
* **Xử lý (Backend/Inference):** Tích hợp Hugging Face API để gọi model không cần tốn tài nguyên local.
* **Hướng tiếp cận AI:** Tập trung vào **Intent Filtering (Phân loại ý định)** để điều hướng luồng xử lý người dùng chính xác (ví dụ: người dùng muốn hỏi thông tin vs. người dùng muốn xem review), đảm bảo độ tin cậy của phản hồi thay vì sử dụng Agent tự trị hoàn toàn.

## 2. Kiến trúc Tổng quát (System Pipeline)
Hệ thống được thiết kế theo luồng xử lý tuần tự (Sequential Pipeline):

1.  **Input Layer:** Streamlit UI nhận text input/review từ người dùng.
2.  **Intent & NER Layer (Nâng cao):** Đi qua mô hình NLP để xác định ý định (hỏi đáp, tìm địa điểm) và trích xuất thực thể (Tên địa danh, thời gian).
3.  **Routing Layer:** Dựa vào intent, điều phối request tới các module chức năng tương ứng.
4.  **Processing Modules:**
    * *Module 1:* Xử lý hội thoại cơ bản (LLM Chat).
    * *Module 2:* Phân tích cảm xúc theo khía cạnh (Aspect-Based Sentiment Analysis - ABSA).
    * *Module 3:* Phát hiện chủ đề (Topic Modeling) từ các đoạn review du lịch dài.
5.  **Output Layer:** Trả kết quả đã phân tích (văn bản, biểu đồ) về Streamlit UI.

## 3. Thiết lập Môi trường và Hugging Face Inference Providers
### 3.1. Môi trường phát triển (macOS / Unix)
Cấu trúc quản lý môi trường ảo độc lập:
```bash
# Tạo môi trường bằng micromamba
micromamba create -n mytravelhelper python=3.11

# Kích hoạt môi trường
micromamba activate mytravelhelper

# Cài đặt thư viện từ requirements.txt
pip install -r requirements.txt
```

```text
MyTravelHelper/
├── requirements.txt         # Chứa danh sách thư viện (streamlit, huggingface_hub, python-dotenv,...)
├── app.py                   # File chạy chính của giao diện Streamlit
├── modules/                 # Thư mục chứa các code xử lý logic tách riêng
│   ├── inference.py         # Các hàm gọi Hugging Face API
│   ├── nlp_tasks.py         # Hàm xử lý Intent, NER, Sentiment, Topic
│   └── utils.py             # Hàm phụ trợ (load config, xử lý text)
├── .env.example             # File mẫu chứa cấu trúc biến môi trường
├── notebook.ipynb           # Notebook trình bày toàn bộ quy trình, phân tích và test
└── README.md                # Hướng dẫn chạy ứng dụng
```

### 3.2. Cấu hình Hugging Face
Sử dụng huggingface_hub library.

Thiết lập token qua file `.env` để bảo mật: `HF_TOKEN=<your_token>`.

## 4. Lựa chọn Model (Model Selection Strategy)
Dựa trên yêu cầu của bài tập và giới hạn của Inference API, dưới đây là danh sách các model dự kiến:

* **Text Generation / Chat:** `mistralai/Mistral-7B-Instruct-v0.2` (Tốc độ phản hồi nhanh, chất lượng tốt cho RAG/Chat).

* **Intent Classification & NER:** `dslim/bert-base-NER` hoặc zero-shot classification model như `facebook/bart-large-mnli`.

* **Aspect-Based Sentiment Analysis (ABSA):** Sử dụng các mô hình chuyên biệt cho sentiment như `cardiffnlp/twitter-roberta-base-sentiment-latest` kết hợp prompt engineering qua LLM để bóc tách khía cạnh.

* **Topic Modeling:** Có thể dùng LLM để trích xuất hoặc các mô hình sentence-transformers để gom cụm (clustering).

## 5. Kế hoạch Triển khai (Milestones & Execution)
### Phase 1: PoC và Thiết lập Cơ bản (Notebook)
* [x] Khởi tạo Jupyter Notebook (notebook.ipynb).

* [x] Test kết nối Hugging Face Inference API.

* [x] Viết script gọi thử 1 model LLM cơ bản.

* [x] Trình bày phần Mục tiêu, Pipeline, và Giới thiệu model trực tiếp bằng Markdown trong Notebook.

### Phase 2: Xây dựng Core App (Streamlit)
* [x] Cài đặt khung giao diện Streamlit (app.py).

* [x] Thiết kế các tab chức năng: "Chatbot Du lịch", "Phân tích Review".

* [x] Tích hợp tính năng Chat cơ bản (Test cơ bản hoạt động).

### Phase 3: Phát triển Tính năng Nâng cao (Advanced Modules)
* [x] Phân loại ý định & NER: Xây dựng hàm `extract_intent_and_entities(text)`.

* [x] Phân tích cảm xúc đa khía cạnh: Xây dựng hàm `analyze_sentiment_aspects(review)`. Khía cạnh ví dụ: Dịch vụ, Vị trí, Giá cả, Tiện nghi.

* [x] Phát hiện chủ đề: Xây dựng luồng trích xuất keyword/topic từ danh sách các review.

### Phase 4: Đóng gói và Bàn giao
* [x] Refactor code, tách các module xử lý AI ra khỏi file UI.

* [x] Đóng băng dependencies vào requirements.txt.

* [x] Kiểm thử toàn diện các luồng.
