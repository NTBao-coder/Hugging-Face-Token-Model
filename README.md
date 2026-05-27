# MyTravelHelper v2.0 — Trợ lý du lịch đa ngôn ngữ

**MyTravelHelper** là ứng dụng NLP/AI hỗ trợ phân tích và tư vấn du lịch, xây dựng bằng **Streamlit** và **Hugging Face Inference Providers**. Phiên bản v2.0 nâng cấp hệ thống từ pipeline tiếng Anh sang pipeline **đa ngôn ngữ Việt - Anh** theo chiến lược **Translate-then-Process**.

Ứng dụng vẫn giữ các model lõi của v1.0, đồng thời bổ sung lớp phát hiện ngôn ngữ, dịch VI ↔ EN, mapping nhãn tiếng Việt và tab dịch thuật riêng để phục vụ người dùng Việt Nam.

---

## Tính năng đã triển khai

### 1. Hỗ trợ tiếng Việt và tiếng Anh

- Tự động phát hiện input tiếng Việt/tiếng Anh.
- Nếu input là tiếng Việt, hệ thống dịch sang tiếng Anh trước khi gọi model NLP tiếng Anh.
- Kết quả được map về nhãn tiếng Việt để hiển thị dễ hiểu.
- App hiển thị bản dịch tiếng Anh được dùng cho model, giúp người dùng kiểm tra pipeline minh bạch hơn.

### 2. Translation Layer

- File chính: `modules/translation.py`
- Hỗ trợ các backend:
  - `googletrans==4.0.0-rc1` cho demo/dev không cần API key.
  - `google-cloud-translate` cho production khi có Google Cloud credentials.
  - Mock fallback offline để app không crash khi thiếu mạng/API.
- Có `batch_translate()` cho danh sách review.
- Có cache trong phiên chạy qua `lru_cache`.

### 3. Language Detection

- File chính: `utils/language_detect.py`
- Kết hợp heuristic tiếng Việt và detect từ translation backend.
- Nhận diện tốt các câu có dấu tiếng Việt hoặc từ khóa du lịch phổ biến như `phòng`, `khách sạn`, `nhân viên`, `đặt`, `thời tiết`.

### 4. Label Mapping tiếng Việt

- File chính:
  - `utils/label_mapper.py`
  - `config/vi_labels.json`
  - `config/travel_aspects_vi.json`
- Mapping đã có cho:
  - Sentiment: `POSITIVE`, `NEGATIVE`, `NEUTRAL`
  - Intent: đặt khách sạn, tìm nhà hàng, hỏi đường, hỏi thời tiết...
  - Aspect: phòng, vệ sinh, nhân viên, dịch vụ, vị trí, đồ ăn...
  - Entity type: địa điểm, thời gian, ngân sách, khoảng thời gian...

### 5. Phân tích cảm xúc và ABSA

- File chính: `modules/sentiment.py`
- Model sử dụng:
  - Basic sentiment: `cardiffnlp/twitter-roberta-base-sentiment-latest`
  - ABSA: `yangheng/deberta-v3-base-absa-v1.1`
- Luồng v2:

```text
VI review → detect language → translate VI to EN → sentiment/ABSA model → map label/aspect to VI
```

- Có heuristic fallback khi không có `HF_TOKEN` hoặc API lỗi.

### 6. Intent Classification và Hybrid NER

- File chính: `modules/intent_ner.py`
- Model sử dụng:
  - Intent: `facebook/bart-large-mnli`
  - NER: `dslim/bert-base-NER`
- Rule-based fallback hỗ trợ:
  - Địa điểm: `Đà Nẵng`, `Hội An`, `Hà Nội`, `Phú Quốc`, ...
  - Ngày tháng: `20/12`, `ngày 20/12`, `thứ sáu tới`
  - Thời lượng: `2 đêm`, `3 ngày`
  - Ngân sách: `5 triệu`, `500k`, `USD`
- Kết quả trả thêm nhãn tiếng Việt như `ĐỊA ĐIỂM`, `THỜI GIAN`, `NGÂN SÁCH`.

### 7. Topic Detection cho review tiếng Việt

- File chính: `modules/topic.py`
- Model/phương pháp:
  - `BERTopic` + `sentence-transformers`
  - Fallback: KMeans + TF-IDF
  - Auto-label: BART MNLI hoặc keyword fallback
- Luồng v2:

```text
Batch review VI/EN → detect từng review → translate VI to EN → BERTopic/KMeans → map topic label to VI
```

- Có file mẫu tiếng Việt: `data/sample_reviews_vi.json`.

### 8. Streamlit App v2

- File chính: `app.py`
- Các tab hiện có:
  - Trợ lý tư vấn & NLU
  - Phân tích cảm xúc khía cạnh
  - Gom cụm chủ đề review
  - Dịch thuật EN ↔ VI
  - Kiến trúc hệ thống
- Sidebar đã cập nhật lên phiên bản `2.0.0 Multilingual`.

### 9. Component React/Tailwind phụ

- File: `components/TravelDestinationCard.tsx`
- Component hiển thị thẻ địa điểm du lịch gồm:
  - Hình ảnh
  - Tên địa danh
  - Đánh giá sao
  - Số lượt đánh giá tùy chọn
  - Button `Khám phá ngay`
- Style bám theo token từ `Design.md`: Rausch `#ff385c`, active `#e00b41`, card bo `14px`, button bo `8px`, text ink `#222222`.

---

## Cấu trúc dự án

```text
MyTravelHelper/
├── app.py
├── requirements.txt
├── README.md
├── EVALUATION.md
├── MyTravelHelper_Project_Plan.md
├── MyTravelHelper_v2_Multilingual_Plan.md
├── notebook.ipynb
├── .env.example
├── assets/
│   ├── screenshot_chatbot.jpg
│   ├── screenshot_pipeline.jpg
│   ├── screenshot_sentiment.jpg
│   ├── screenshot_topics_1.jpg
│   └── screenshot_topics_2.jpg
├── components/
│   └── TravelDestinationCard.tsx
├── config/
│   ├── vi_labels.json
│   └── travel_aspects_vi.json
├── data/
│   ├── sample_reviews.json
│   └── sample_reviews_vi.json
├── modules/
│   ├── __init__.py
│   ├── intent_ner.py
│   ├── sentiment.py
│   ├── topic.py
│   └── translation.py
└── utils/
    ├── __init__.py
    ├── display.py
    ├── label_mapper.py
    ├── language_detect.py
    └── preprocessing.py
```

---

## Công nghệ và model sử dụng

| Nhóm | Công nghệ / Model |
|---|---|
| UI | Streamlit |
| HF client | `huggingface_hub.InferenceClient` |
| Translation | `googletrans`, `google-cloud-translate`, mock fallback |
| Basic sentiment | `cardiffnlp/twitter-roberta-base-sentiment-latest` |
| ABSA | `yangheng/deberta-v3-base-absa-v1.1` |
| Intent | `facebook/bart-large-mnli` |
| NER | `dslim/bert-base-NER` + regex/rule-based fallback |
| Topic modeling | BERTopic, sentence-transformers, KMeans + TF-IDF fallback |
| Visualization | Plotly, Altair, Streamlit native charts |
| Data | pandas, numpy, scikit-learn |

---

## Cài đặt

### 1. Tạo môi trường Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Có thể dùng `micromamba` nếu muốn:

```bash
micromamba create -n mytravelhelper python=3.11
micromamba activate mytravelhelper
pip install -r requirements.txt
```

### 2. Cấu hình Hugging Face token

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Điền token:

```env
HF_TOKEN=hf_your_actual_token_here
```

Nếu chưa có `HF_TOKEN`, app vẫn chạy bằng heuristic fallback để demo luồng chính.

### 3. Cấu hình Google Translate tùy chọn

Mặc định app ưu tiên `googletrans` cho demo vì không cần API key. Nếu muốn dùng Google Cloud Translate, thêm credentials vào `.env`:

```env
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
```

Hoặc cấu hình theo môi trường Google Cloud đang dùng.

---

## Chạy ứng dụng

```bash
streamlit run app.py
```

Sau đó mở:

```text
http://localhost:8501
```

---

## Kiểm thử nhanh

### 1. Kiểm tra cú pháp/import

```bash
python3 -m compileall app.py modules utils
```

### 2. Smoke test multilingual

```bash
python3 -c "from modules.sentiment import analyze_sentiment; from modules.intent_ner import classify_intent, extract_entities; from modules.topic import detect_topics_zeroshot; print(analyze_sentiment('Phòng sạch, nhân viên thân thiện', mode='basic')['label_vi']); print(classify_intent('Tôi muốn đặt khách sạn ở Đà Nẵng 2 đêm')['intent_vi']); print([e['entity_type_vi'] for e in extract_entities('Tôi muốn đặt khách sạn ở Đà Nẵng 2 đêm ngày 20/12 với 5 triệu')]); print(detect_topics_zeroshot('Bữa sáng ngon và nhân viên thân thiện')['topic'])"
```

Kết quả kỳ vọng:

```text
TÍCH CỰC
đặt khách sạn
['ĐỊA ĐIỂM', 'KHOẢNG THỜI GIAN', 'THỜI GIAN', 'NGÂN SÁCH']
Ẩm thực địa phương
```

---

## Ví dụ sử dụng module

```python
from modules.sentiment import analyze_sentiment
from modules.intent_ner import classify_intent, extract_entities
from modules.topic import detect_topics_zeroshot

review = "Phòng rất sạch nhưng nhân viên hơi chậm."
print(analyze_sentiment(review, mode="basic"))
print(analyze_sentiment(review, mode="absa"))

query = "Tôi muốn đặt khách sạn ở Đà Nẵng 2 đêm ngày 20/12 với 5 triệu"
print(classify_intent(query))
print(extract_entities(query))

print(detect_topics_zeroshot("Bữa sáng ngon và vị trí gần biển."))
```

---

## Tài liệu liên quan

- `MyTravelHelper_Project_Plan.md`: kế hoạch v1.0.
- `MyTravelHelper_v2_Multilingual_Plan.md`: kế hoạch nâng cấp v2.0 multilingual.
- `EVALUATION.md`: đánh giá triển khai thực tế so với hai plan.
- `Design.md`: design tokens và quy tắc UI dùng cho component React/Tailwind.
- `notebook.ipynb`: notebook trình bày quy trình và thử nghiệm.

---

## Trạng thái hiện tại

MyTravelHelper v2.0 hiện đạt mức **prototype/local demo**:

- Đã có pipeline multilingual VI/EN cho các tác vụ chính.
- Đã có fallback để demo khi thiếu token/API.
- Đã kiểm tra compile và smoke test cơ bản.
- Chưa xác thực đầy đủ chất lượng Google Translate và Hugging Face API thật trong môi trường hiện tại.

Để chuẩn bị nộp/demo chắc hơn, nên chạy app với `HF_TOKEN`, kiểm tra backend dịch thật và cập nhật notebook với output v2 đã lưu.
