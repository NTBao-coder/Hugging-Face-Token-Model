import os
import sys

# Load environmental variables
from dotenv import load_dotenv
load_dotenv()

# Initialize utilities and services
from modules.translation import TranslationService
from utils.language_detect import LanguageDetector
from utils.label_mapper import LabelMapper
from modules.sentiment import analyze_sentiment
from modules.intent_ner import classify_intent, extract_entities, travel_chat
from modules.topic import detect_topics_bertopic

def run_tests():
    print("=== STARTING MULTILINGUAL V2 TESTS ===")
    
    translator = TranslationService()
    detector = LanguageDetector()
    mapper = LabelMapper()
    
    # 1. Test Language Detection
    print("\n[Test 1] Language Detection:")
    samples = {
        "Tôi muốn đi du lịch Vũng Tàu": "vi",
        "The hotel was awesome and clean": "en",
        "Nice food, friendly service": "en"
    }
    for text, expected in samples.items():
        detected = detector.detect(text)
        print(f"  Text: '{text}' -> Detected: {detected} (Expected: {expected})")
        assert detected == expected, f"Language detection mismatch for '{text}': expected {expected}, got {detected}"
    print("  => Test 1 Passed!")

    # 2. Test Translation Wrapper
    print("\n[Test 2] Translation Wrapper:")
    vi_text = "Phòng tắm rất rộng rãi"
    en_translation = translator.translate(vi_text, src="vi", dest="en")
    print(f"  VI: '{vi_text}' -> EN: '{en_translation}'")
    assert "room" in en_translation.lower() or "bath" in en_translation.lower() or "spacious" in en_translation.lower(), "Translation output seems incorrect."
    
    en_text = "The price was too high"
    vi_translation = translator.translate(en_text, src="en", dest="vi")
    print(f"  EN: '{en_text}' -> VI: '{vi_translation}'")
    assert "giá" in vi_translation.lower() or "đắt" in vi_translation.lower() or "cao" in vi_translation.lower(), "Translation output seems incorrect."
    print("  => Test 2 Passed!")

    # 3. Test Sentiment & ABSA (Vietnamese)
    print("\n[Test 3] Sentiment & ABSA:")
    sample_review = "Phòng ngủ sạch sẽ nhưng đồ ăn sáng hơi dở."
    overall = analyze_sentiment(sample_review, mode="basic")
    print(f"  Overall Sentiment: {overall}")
    assert "label_vi" in overall, "Vietnamese label is missing from sentiment output."
    
    absa_results = analyze_sentiment(sample_review, mode="absa")
    print("  ABSA Results:")
    for res in absa_results:
        print(f"    Aspect: {res['aspect_vi']} ({res['aspect']}) -> Sentiment: {res['sentiment_vi']} ({res['sentiment']})")
        assert "aspect_vi" in res and "sentiment_vi" in res, "ABSA results must contain bilingual fields."
    print("  => Test 3 Passed!")

    # 4. Test Intent & NER Alignment
    print("\n[Test 4] Intent & NER Alignment:")
    query = "Tôi muốn đi du lịch Nha Trang 4 ngày với ngân sách 10 triệu đồng"
    intent = classify_intent(query)
    print(f"  Intent: {intent}")
    assert "intent_vi" in intent, "Intent classification missing Vietnamese translation mapping."
    
    entities = extract_entities(query)
    print("  Entities:")
    loc_found = False
    budget_found = False
    for ent in entities:
        print(f"    Word: '{ent['word']}' -> Type: {ent['entity_type_vi']} ({ent['entity_type']}) [Source: {ent['source']}]")
        assert "entity_type_vi" in ent, "Entity missing Vietnamese type description."
        if ent["entity_type"] == "LOCATION" and "nha trang" in ent["word"].lower():
            loc_found = True
        if ent["entity_type"] == "BUDGET" and "10 triệu" in ent["word"].lower():
            budget_found = True
            
    # Verify name preservation of locations & budgets
    assert loc_found, "Failed to extract or align 'Nha Trang' LOCATION entity."
    assert budget_found, "Failed to extract or align '10 triệu' BUDGET entity."
    print("  => Test 4 Passed!")

    # 5. Test Topic Clustering
    print("\n[Test 5] Topic Clustering:")
    docs = [
        "Bãi biển Nha Trang sạch và rất đẹp, cát vàng mịn.",
        "Resort có hồ bơi lớn ngay cạnh bãi tắm thoải mái.",
        "Bữa sáng nghèo nàn, thái độ nhân viên dọn phòng rất kém.",
        "Dịch vụ spa và phòng massage có giá khá đắt đỏ.",
        "Giá vé tham quan và chi phí đi taxi đắt đỏ.",
        "Buffet nhà hàng phục vụ nhiều món ăn ngon."
    ]
    topics, model = detect_topics_bertopic(docs)
    info = model.get_topic_info()
    print("  Topics:")
    for index, row in info.iterrows():
        print(f"    Topic {row['Topic']}: Name: {row['Name']} | Represented Words: {row['Representation']}")
    print("  => Test 5 Passed!")

    print("\n=== ALL MULTILINGUAL V2 TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_tests()
