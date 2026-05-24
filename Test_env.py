import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load các biến từ file .env vào môi trường hệ thống
load_dotenv()

# Lấy token
hf_token = os.getenv("HF_TOKEN")

if hf_token:
    print("Đã tìm thấy Token!")
    # Khởi tạo client để test thử
    client = InferenceClient(token=hf_token)
    try:
        # Gọi thử một model nhỏ như distilbert-sst2 đã định nghĩa trong kế hoạch
        result = client.text_classification(
            "The hotel was absolutely amazing!",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        print("Test Inference thành công:", result)
    except Exception as e:
        print("Lỗi khi gọi API:", e)
else:
    print("Lỗi: Không tìm thấy biến HF_TOKEN trong file .env")