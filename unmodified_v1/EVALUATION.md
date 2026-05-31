# Đánh giá tiến độ dự án MyTravelHelper

## 1. Tổng quan

Dự án đã có bản PoC chạy được bằng Streamlit, có notebook trình bày quy trình xây dựng ứng dụng và có các module Python tách riêng cho phần Hugging Face, xử lý NLP và tiện ích. Ứng dụng hiện hỗ trợ cả chế độ gọi Hugging Face Inference Providers khi có `HF_TOKEN` và chế độ fallback cục bộ để demo khi chưa cấu hình token.

## 2. Tính năng đã hoàn thành

| Hạng mục | Mô tả đã làm | Mức độ hoàn thành |
|---|---|---|
| Mục tiêu và phân tích yêu cầu | Đã trình bày trong `plan.md`, `README.md` và `notebook.ipynb`. | Hoàn thành |
| Kiến trúc tổng quát | Đã mô tả pipeline input, intent/NER, routing, processing modules, output. | Hoàn thành |
| Thiết lập môi trường | Đã chuyển sang hướng dẫn dùng `micromamba`, có `requirements.txt` và `.env.example`. | Hoàn thành |
| Tích hợp Hugging Face | Đã tạo `HuggingFaceService` dùng `huggingface_hub.InferenceClient`, hỗ trợ chat, zero-shot classification, NER và sentiment. | Hoàn thành mức PoC |
| Streamlit app | Đã có `app.py` với các tab: Chatbot du lịch, Phân tích review, Intent & NER, Topic, Pipeline. | Hoàn thành mức PoC |
| Notebook bài nộp | Đã có `notebook.ipynb` trình bày quy trình, model, setup và các đoạn test cơ bản. | Hoàn thành |
| Phân tích cảm xúc theo khía cạnh | Đã nhận diện các khía cạnh như Dịch vụ, Vị trí, Giá cả, Tiện nghi, Ẩm thực, Vệ sinh bằng rule-based heuristic. | Hoàn thành mức demo |
| Phân loại ý định và trích xuất thực thể | Đã phân loại intent bằng keyword/fallback và có thể kết hợp zero-shot Hugging Face. Entity gồm location, date, duration, budget. | Hoàn thành mức demo |
| Phát hiện chủ đề review | Đã nhận diện topic theo nhóm từ khóa và xuất bảng/biểu đồ trong Streamlit. | Hoàn thành mức demo |
| Kiểm thử cơ bản | Đã kiểm tra cú pháp Python, JSON notebook, test hàm NLP cục bộ và HTTP Streamlit. | Hoàn thành |

## 3. Mức độ hoàn thành theo yêu cầu đề bài

| Yêu cầu đề bài | Trạng thái | Ghi chú |
|---|---|---|
| Trình bày bằng notebook quy trình xây dựng ứng dụng | Đạt | Notebook đã có các phần chính theo yêu cầu. |
| Sử dụng Streamlit cho giao diện | Đạt | App chạy tại `app.py`. |
| Mục tiêu, phân tích yêu cầu | Đạt | Có trong notebook và plan. |
| Mô tả kiến trúc tổng quát | Đạt | Có pipeline Mermaid. |
| Thiết lập Inference Providers của Hugging Face | Đạt | Có `.env.example`, `HF_TOKEN`, `InferenceClient`. |
| Giới thiệu model sử dụng | Đạt | Có danh sách model trong notebook/app/sidebar. |
| Test cơ bản thiết lập môi trường | Đạt | Có lệnh kiểm thử và cell healthcheck. |
| Chạy ứng dụng, kiểm thử cơ bản hoạt động | Đạt | App đã chạy được trên localhost. |
| Phân tích cảm xúc theo khía cạnh | Đạt mức demo | Logic hiện tại chủ yếu rule-based. |
| Phân loại ý định và trích xuất thực thể | Đạt mức demo | Có thể nâng cấp thêm model NER tiếng Việt tốt hơn. |
| Phát hiện chủ đề trong review du lịch | Đạt mức demo | Hiện dùng keyword/topic heuristic. |

## 4. Rủi ro có thể có

### 4.1. Rủi ro về Hugging Face API

- Nếu chưa có `HF_TOKEN`, app chỉ chạy fallback cục bộ, chưa chứng minh được chất lượng phản hồi từ model thật.
- Một số model có thể yêu cầu quyền truy cập, đang tải lạnh, bị rate limit hoặc thay đổi endpoint.
- API của `huggingface_hub` có thể khác nhau theo phiên bản, nên cần giữ dependency tương đối mới như trong `requirements.txt`.

### 4.2. Rủi ro về chất lượng NLP

- Phân tích cảm xúc theo khía cạnh hiện dựa nhiều vào từ khóa, dễ sai với câu phủ định, mỉa mai hoặc ngữ cảnh phức tạp.
- Intent classification fallback có thể nhầm giữa các ý định gần nhau, ví dụ hỏi địa điểm và lập lịch trình.
- NER rule-based mới nhận diện được một số địa danh, thời lượng và ngân sách phổ biến; chưa bao phủ toàn bộ thực thể du lịch.
- Topic detection bằng keyword chưa phải topic modeling thật như clustering/embedding, nên kết quả phù hợp demo hơn là đánh giá sản phẩm hoàn chỉnh.

### 4.3. Rủi ro về giao diện và trải nghiệm

- Giao diện Streamlit hiện ở mức PoC, chưa có lưu lịch sử chat, quản lý session nâng cao hoặc xuất báo cáo phân tích.
- Kết quả JSON ở tab Intent & NER hữu ích cho kiểm thử nhưng chưa thân thiện hoàn toàn với người dùng cuối.

### 4.4. Rủi ro về bài nộp

- Nếu giảng viên yêu cầu bắt buộc gọi model thật trong lúc demo, cần chuẩn bị sẵn `HF_TOKEN` và kiểm tra internet/API trước khi trình bày.
- Nếu muốn đạt điểm cao phần nâng cao, nên bổ sung thêm ví dụ chạy thực tế trong notebook, kèm output đã lưu.
- Notebook hiện là quy trình trình bày và test; nếu cần, có thể execute toàn bộ cell để lưu output minh chứng.

## 5. Đề xuất cải thiện tiếp theo

1. Chạy notebook với `HF_TOKEN` thật và lưu output minh chứng.
2. Thay ABSA heuristic bằng prompt LLM hoặc model sentiment phù hợp tiếng Việt hơn.
3. Bổ sung danh sách địa danh và thực thể du lịch Việt Nam để NER fallback tốt hơn.
4. Dùng embedding hoặc `sentence-transformers` để topic detection gần với topic modeling hơn.
5. Thêm ảnh chụp màn hình app hoặc đoạn hướng dẫn demo vào README.

## 6. Hướng dẫn chạy dự án

### 6.1. Tạo môi trường

```bash
micromamba create -n mytravelhelper python=3.11
micromamba activate mytravelhelper
pip install -r requirements.txt
```

### 6.2. Cấu hình Hugging Face token

Sao chép file `.env.example` thành `.env` và điền token:

```bash
cp .env.example .env
```

Nội dung file `.env`:

```bash
HF_TOKEN=hf_your_token_here
```

Nếu chưa có `HF_TOKEN`, ứng dụng vẫn chạy được bằng fallback cục bộ để demo các luồng chính.

### 6.3. Chạy ứng dụng Streamlit

```bash
streamlit run app.py
```

Sau khi chạy, mở địa chỉ:

```text
http://localhost:8501
```

### 6.4. Chạy notebook

Mở file `notebook.ipynb` bằng Jupyter Notebook, JupyterLab hoặc VS Code, sau đó chạy lần lượt các cell để xem phần trình bày và test cơ bản.

Nếu muốn chạy JupyterLab:

```bash
jupyter lab notebook.ipynb
```

### 6.5. Kiểm thử nhanh bằng terminal

```bash
python -m py_compile app.py modules/*.py
```

Có thể kiểm tra nhanh các hàm NLP cục bộ:

```bash
python - <<'PY'
from modules.nlp_tasks import analyze_sentiment_aspects, detect_topics, extract_intent_and_entities

print(extract_intent_and_entities("Mình muốn đi Hội An 3 ngày với ngân sách 4 triệu"))
print(analyze_sentiment_aspects("Phòng sạch, vị trí gần biển nhưng giá hơi cao."))
print(detect_topics(["Biển đẹp, hải sản ngon.", "Khách sạn gần trung tâm, phòng sạch."]))
PY
```
