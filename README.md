# Hugging-Face-Token-Model
### Bài tập
Trình bày bằng notebook quy trình xây dựng ứng dụng MyTravelHelper sử dụng Streamlit cho giao diện.

Cần có các nội dung và chức năng sau:
- Mục tiêu, phân tích yêu cầu.
- Mô tả kiến trúc tổng quát (sơ đồ pipeline)
- Quá trình thiết lập để sử dụng Inference Providers của Hugging Face.
- Giới thiệu các model sẽ sử dụng.
- Test cơ bản thiết lập môi trường.
- Chạy ứng dụng, kiểm thử cơ bản hoạt động, các chức năng mở rộng nếu có.

Phần nâng cao (mỗi mục tính 2 điểm):
- Phân tích cảm xúc đối với đánh giá du lịch (có phân tích dựa trên khía cạnh).
- Phân loại ý định và trích xuất thực thể từ yêu cầu của người dùng..
- Phát hiện các chủ đề được nhắc đến trong review du lịch.

Bài nộp gồm: notebook, các file code python, các module nếu có tách riêng (khi này cần có file requirements.txt).

## MyTravelHelper

MyTravelHelper là ứng dụng trợ lý du lịch dùng Streamlit cho giao diện và Hugging Face Inference Providers cho các tác vụ NLP/LLM. App có thể chạy ở chế độ fallback cục bộ khi chưa cấu hình `HF_TOKEN`, giúp kiểm thử cơ bản các chức năng trước khi gọi API thật.

### Cấu trúc dự án

```text
.
├── app.py
├── modules/
│   ├── inference.py
│   ├── nlp_tasks.py
│   └── utils.py
├── notebook.ipynb
├── requirements.txt
├── .env.example
├── plan.md
└── README.md
```

### Thiết lập môi trường

```bash
micromamba create -n mytravelhelper python=3.11
micromamba activate mytravelhelper
pip install -r requirements.txt
```

Tạo file `.env` từ `.env.example` và điền Hugging Face token:

```bash
HF_TOKEN=hf_your_token_here
```

### Chạy ứng dụng

```bash
streamlit run app.py
```

Ứng dụng gồm các tab:

- **Chatbot du lịch:** tư vấn lịch trình/câu hỏi du lịch.
- **Phân tích review:** phân tích cảm xúc theo khía cạnh như dịch vụ, vị trí, giá cả, tiện nghi.
- **Intent & NER:** phân loại ý định và trích xuất thực thể như địa điểm, thời gian, ngân sách.
- **Topic:** phát hiện chủ đề nổi bật trong nhiều review.
- **Pipeline:** mô tả kiến trúc tổng quát của hệ thống.

### Kiểm thử nhanh

```bash
python -m py_compile app.py modules/*.py
```

Notebook `notebook.ipynb` trình bày quy trình xây dựng ứng dụng, lựa chọn model và các đoạn test cơ bản theo yêu cầu bài tập.
