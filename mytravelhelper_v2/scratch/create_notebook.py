import json
import os

notebook = {
    "cells": [],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

def add_markdown(text):
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.split("\n")]
    })

def add_code(code_lines):
    notebook["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in code_lines.split("\n")]
    })

# --- CELL 0: TITLE ---
add_markdown("""# MyTravelHelper v2.0 — Kế hoạch Nâng cấp Đa ngôn ngữ (Multilingual Edition)

Jupyter Notebook này trình bày quy trình triển khai và kiểm thử hệ thống trợ lý du lịch **MyTravelHelper v2.0**, bổ sung khả năng xử lý đa ngôn ngữ **English & Vietnamese** dựa trên chiến lược **Translate-then-Process**.

## 1. Tổng quan & So sánh v1.0 vs v2.0

| # | Mục tiêu | Baseline v1.0 | Target v2.0 |
|---|---|---|---|
| 1 | Input language | Tiếng Anh only | **Tiếng Việt + Tiếng Anh** |
| 2 | ABSA | Tiếng Anh | **Tiếng Việt input, EN pipeline** |
| 3 | Intent + NER | Tiếng Anh | **Tiếng Việt input, EN pipeline** |
| 4 | Topic Detection | Tiếng Anh | **Tiếng Việt input, EN pipeline** |
| 5 | Translation tool | Không có | **Tab dịch EN ↔ VI tự do** |
| 6 | Translation engine | Không có | **Google Translate API / googletrans** |
""")

# --- CELL 1: ARCHITECTURE ---
add_markdown("""## 2. Kiến trúc tổng quát v2.0

Sơ đồ dưới đây minh họa luồng xử lý tuần tự (Sequential Pipeline) có tích hợp lớp Dịch thuật (Translation Layer) & Ánh xạ nhãn (Label Mapping):

```mermaid
flowchart TD
    A[User Input\\nVI hoặc EN] --> B[Language Detection\\nlangdetect]
    B -->|Tiếng Việt| C[★ Google Translate\\nVI → EN]
    B -->|Tiếng Anh| D[Bypass Translation]
    C --> E[English Text]
    D --> E
    E --> F{Task Type?}
    F -->|Review| G[Sentiment/ABSA\\ndeberta-v3-absa]
    F -->|Query| H[Intent + NER\\nbart-mnli + bert-NER]
    F -->|Batch docs| I[Topic Detection\\nBERTopic + bart-mnli]
    G --> J[★ Result Translator\\nlabel_mapper.py]
    H --> J
    I --> J
    J --> K[★ Bilingual Display\\nEN + VI side by side]

    L[Tab 4: Translation Tool] --> M[★ TranslationService\\ngoogletrans wrapper]
    M -->|EN→VI| N[Vietnamese Output]
    M -->|VI→EN| O[English Output]
    N --> P[★ Swap Button ⇄]
    O --> P
    P --> M
```
""")

# --- CELL 2: SYSTEM SETUP ---
add_markdown("""## 3. Thiết lập Google Translate API & Utilities

Định nghĩa lớp `TranslationService` kết nối dịch thuật từ `googletrans` (không cần API key) và fallback qua `deep_translator` khi gặp lỗi rate-limit.
""")

# --- CELL 3: CODE FOR TRANSLATION SERVICE ---
add_code("""# Nạp các thư viện chính và thiết lập môi trường
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Thêm đường dẫn root vào python path
sys.path.append(os.getcwd())

# Import dịch vụ và các module tiện ích v2.0
from modules.translation import TranslationService
from utils.language_detect import LanguageDetector
from utils.label_mapper import LabelMapper

translator = TranslationService()
detector = LanguageDetector()
mapper = LabelMapper()

print("Khởi tạo dịch vụ và lớp Mapping thành công!")
""")

# --- CELL 4: ENVIRONMENT TESTS ---
add_markdown("""## 4. Kiểm thử cơ bản môi trường (5 bộ test)

### Test 1: Kiểm tra cài đặt packages
""")

add_code("""# Test 1: Import kiểm tra các packages mới
packages = ["googletrans", "deep_translator", "langdetect", "nltk"]
for pkg in packages:
    try:
        __import__(pkg)
        print(f"✅ {pkg} - OK")
    except ImportError:
        print(f"❌ {pkg} - Chưa cài đặt!")
""")

# --- CELL 5: TEST 2 ---
add_markdown("""### Test 2: Dịch đơn giản VI ↔ EN""")
add_code("""# Test 2: Dịch 2 chiều đơn giản
texts = [
    ("Phòng khách sạn rất sạch sẽ và thoáng mát", "vi", "en"),
    ("The staff was extremely helpful and polite", "en", "vi")
]

for text, src, dest in texts:
    res = translator.translate(text, src=src, dest=dest)
    print(f"[{src.upper()} -> {dest.upper()}] Gốc: {text}")
    print(f"       -> Dịch: {res}\\n")
""")

# --- CELL 6: TEST 3 ---
add_markdown("""### Test 3: Phát hiện ngôn ngữ (Language Detection)""")
add_code("""# Test 3: Kiểm thử tự động nhận dạng ngôn ngữ
samples = [
    "Khách sạn đẹp lắm, vị trí đắc địa ngay sát biển.",
    "Excellent service, clean room and helpful staff.",
    "Tôi muốn book một resort 5 sao ở Phú Quốc vào tháng sau"
]

for s in samples:
    lang = detector.detect(s)
    lang_name = "Tiếng Việt 🇻🇳" if lang == "vi" else "Tiếng Anh 🇺🇸"
    print(f"Văn bản: '{s}'")
    print(f"  -> Nhận diện: {lang_name} ({lang})\\n")
""")

# --- CELL 7: TEST 4 ---
add_markdown("""### Test 4: Batch dịch (Batch Translation)""")
add_code("""# Test 4: Dịch đồng loạt danh sách câu
reviews_vi = [
    "Phòng sạch, nhân viên tốt",
    "Giá phòng đắt đỏ so với chất lượng",
    "Buffet sáng ngon miệng và nhiều món"
]

results = translator.batch_translate(reviews_vi, src="vi", dest="en")
for vi, en in zip(reviews_vi, results):
    print(f"VI: {vi}")
    print(f"EN: {en}\\n")
""")

# --- CELL 8: TEST 5 ---
add_markdown("""### Test 5: Tích hợp Translation + NLP End-to-End""")
add_code("""# Test 5: Dịch câu tiếng Việt -> Chạy mô hình Sentiment/ABSA -> Map kết quả về tiếng Việt
from modules.sentiment import analyze_sentiment

review_vi = "Nhân viên thân thiện nhưng wifi quá chậm và chập chờn."
print(f"Review gốc: {review_vi}")

# Chạy ABSA (Hệ thống tự dịch và xử lý)
results = analyze_sentiment(review_vi, mode="absa")
print("\\n--- KẾT QUẢ PHÂN TÍCH ABSA SONG NGỮ ---")
for res in results:
    print(f"Khía cạnh: {res['aspect_vi']} ({res['aspect']})")
    print(f"  Cảm xúc: {res['sentiment_vi']} ({res['sentiment']})")
    print(f"  Độ tin cậy: {res['confidence']}")
    print(f"  Nguồn: {res['source']}\\n")
""")

# --- CELL 9: ADVANCED DEMOS ---
add_markdown("""## 5. Chạy ứng dụng & Hướng dẫn sử dụng Streamlit App v2.0

Để chạy giao diện Streamlit App v2.0 với đầy đủ tính năng đa ngôn ngữ và tab dịch thuật, hãy mở terminal tại thư mục dự án và chạy lệnh sau:

```bash
streamlit run app.py
```

Ứng dụng sẽ mở giao diện tại `http://localhost:8501/` bao gồm 5 tab chức năng:
1. **💬 Trợ Lý Tư Vấn & NLU**: Hỗ trợ nhập câu hỏi tiếng Việt/tiếng Anh, phân tích ý định, thực thể và phản hồi tự động.
2. **📊 Phân Tích Cảm Xúc Khía Cạnh**: Phân tích ABSA trên các review tiếng Việt hoặc tiếng Anh.
3. **🏷️ Gom Cụm Chủ Đề Review**: Gom cụm các reviews tiếng Việt bằng cách dịch batch sang tiếng Anh rồi chạy BERTopic.
4. **🌐 Dịch thuật EN ↔ VI**: Công cụ dịch nhanh 2 chiều với nút đổi chiều thông minh.
5. **⚙️ Kiến Trúc Hệ Thống**: Mermaid pipeline chi tiết.
""")

# --- CELL 10: DEMO ABSA ---
add_markdown("""## 6. Demos chi tiết các tính năng nâng cao (Multilingual NLP)

### 6.1 ABSA Tiếng Việt (Aspect-Based Sentiment Analysis)
""")

add_code("""# 6.1 Demo ABSA tiếng Việt
vi_reviews = [
    "Phòng ngủ rộng rãi, giường êm ái nhưng vệ sinh phòng tắm chưa sạch lắm.",
    "Bữa sáng buffet quá ít món và không có đặc sản địa phương, tuy nhiên hồ bơi rất đẹp."
]

for review in vi_reviews:
    print(f"Review: '{review}'")
    absa_res = analyze_sentiment(review, mode="absa")
    for r in absa_res:
        print(f"  -> aspect: {r['aspect_vi']} ({r['aspect']}) | sentiment: {r['sentiment_vi']} ({r['sentiment']}) | conf: {r['confidence']}")
    print()
""")

# --- CELL 11: DEMO INTENT + NER ---
add_markdown("""### 6.2 Intent + NER Tiếng Việt (Name Preservation)

Nhận diện ý định và trích xuất thực thể, bảo toàn tên riêng địa danh Việt Nam có dấu.
""")

add_code("""# 6.2 Demo Intent và NER tiếng Việt
from modules.intent_ner import classify_intent, extract_entities

queries = [
    "Tôi muốn đặt khách sạn 4 sao ở Đà Nẵng 3 ngày với ngân sách khoảng 6 triệu đồng.",
    "Làm sao để đi từ sân bay Cam Ranh về trung tâm Nha Trang bằng xe bus?"
]

for q in queries:
    print(f"Câu hỏi: '{q}'")
    
    # 1. Intent Classification
    intent = classify_intent(q)
    print(f"  -> Ý định: {intent['intent_vi']} ({intent['intent']}) [Conf: {intent['confidence']}]")
    
    # 2. NER Extraction
    entities = extract_entities(q)
    print("  -> Thực thể trích xuất:")
    for ent in entities:
        print(f"     * Từ: '{ent['word']}' | Loại: {ent['entity_type_vi']} ({ent['entity_type']}) | Nguồn: {ent['source']}")
    print("-" * 50)
""")

# --- CELL 12: DEMO TOPIC DETECTION ---
add_markdown("""### 6.3 Gom cụm chủ đề Tiếng Việt (Topic Detection)""")
add_code("""# 6.3 Demo Gom cụm chủ đề Tiếng Việt
from modules.topic import detect_topics_bertopic

docs_vi = [
    "Bãi biển rất sạch và có bờ cát trắng cực kì thích, bơi lội thoải mái.",
    "Bể bơi vô cực sạch sẽ và view ngắm thành phố rất đẹp.",
    "Giá phòng đắt đỏ nhưng dịch vụ thì chắp vá không tương xứng tí nào.",
    "Chi phí thuê xe máy và ăn uống ở đây quá đắt đỏ.",
    "Bữa sáng buffet ở đây vô cùng ngon miệng và nhiều món ăn đặc sản miền trung.",
    "Nhà hàng phục vụ đồ ăn rất tươi và hợp khẩu vị gia đình tôi."
]

print(f"Chạy gom cụm với {len(docs_vi)} reviews tiếng Việt...")
topics, model = detect_topics_bertopic(docs_vi)

# Đọc bảng thống kê
info = model.get_topic_info()
print("\\n--- BẢNG THỐNG KÊ CHỦ ĐỀ PHÁT HIỆN ĐƯỢC ---")
for index, row in info.iterrows():
    rep_str = ", ".join(row["Representation"])
    print(f"Topic {row['Topic']}: Tên: {row['Name']} | Số lượng: {row['Count']} | Từ khóa: [{rep_str}]")
""")

# --- CELL 13: DEMO TRANSLATION TOOL SWAP ---
add_markdown("""### 6.4 Translation Tool EN ↔ VI (Swap and Auto-translate)""")
add_code("""# 6.4 Demo Translation Tool hoán đổi ngôn ngữ
# Mô phỏng quá trình dịch và đảo ngược ngôn ngữ nguồn-đích
src_text_1 = "Chào mừng bạn đến với ứng dụng trợ lý du lịch MyTravelHelper!"
print(f"Văn bản gốc: {src_text_1}")

# Dịch VI -> EN
translated_1 = translator.translate(src_text_1, src="vi", dest="en")
print(f"Dịch sang EN: {translated_1}")

# Đảo ngược chiều dịch: EN -> VI
src_text_2 = translated_1
translated_2 = translator.translate(src_text_2, src="en", dest="vi")
print(f"Hoán đổi dịch ngược sang VI: {translated_2}")
""")

# Write out the notebook file
notebook_path = "MyTravelHelper_v2_Multilingual.ipynb"
with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

print(f"Đã tạo file {notebook_path} thành công!")
