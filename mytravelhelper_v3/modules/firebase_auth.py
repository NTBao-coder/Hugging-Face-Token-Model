import os
import httpx
from pathlib import Path
from datetime import datetime
# pyrefly: ignore [missing-import]
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv

# Ensure environment variables are loaded
MODULE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_DIR.parent
load_dotenv(PROJECT_ROOT / ".env")

# Path to Firebase Credentials
CRED_PATH = PROJECT_ROOT / "config" / "firebase_credentials.json"

# Initialize Firebase Admin SDK
def init_firebase():
    if not firebase_admin._apps:
        if CRED_PATH.exists():
            cred = credentials.Certificate(str(CRED_PATH))
            firebase_admin.initialize_app(cred)
            print("Firebase Admin initialized successfully using service account.")
        else:
            project_id = os.getenv("FIREBASE_PROJECT_ID", "mytravelhelper-payment")
            try:
                firebase_admin.initialize_app(options={"projectId": project_id})
                print(f"Firebase Admin initialized using project ID: {project_id}")
            except Exception as e:
                print(f"Warning: Firebase Admin failed to initialize: {e}")

# Trigger initialization
init_firebase()

def is_mock_firebase() -> bool:
    """Detect if the application should use local mock Auth due to missing credentials."""
    web_api_key = os.getenv("FIREBASE_WEB_API_KEY")
    return not web_api_key or web_api_key.startswith("your_")

def register_user(email: str, password: str, display_name: str) -> dict:
    """Register a new user in Firebase Auth or local mock database."""
    if is_mock_firebase():
        import uuid
        uid = f"mock_uid_{uuid.uuid4().hex[:8]}"
        user_info = {
            "uid": uid,
            "email": email,
            "display_name": display_name
        }
        
        # Save user to mock database
        from modules.firebase_db import _load_mock_db, _save_mock_db
        mock_db = _load_mock_db()
        mock_db["users"][uid] = {
            "uid": uid,
            "email": email,
            "display_name": display_name,
            "password": password,  # Used to check password during mock login
            "created_at": datetime.now().isoformat(),
            "total_spent": 0.0
        }
        _save_mock_db(mock_db)
        print(f"[Mock Auth] Đăng ký thành công người dùng: {email} (UID: {uid})")
        return user_info
        
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name
        )
        return {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name
        }
    except Exception as e:
        raise ValueError(f"Đăng ký thất bại: {str(e)}")

def login_user(email: str, password: str) -> dict:
    """Log in a user using Firebase Auth REST API or local mock validation."""
    if is_mock_firebase():
        from modules.firebase_db import _load_mock_db
        mock_db = _load_mock_db()
        for uid, user in mock_db["users"].items():
            if user.get("email") == email:
                if user.get("password") == password:
                    print(f"[Mock Auth] Đăng nhập thành công người dùng: {email}")
                    return {
                        "id_token": f"mock_token_{uid}",
                        "refresh_token": f"mock_refresh_{uid}",
                        "uid": uid,
                        "email": email,
                        "display_name": user.get("display_name", "")
                    }
                else:
                    raise ValueError("Mật khẩu không chính xác (Mock Mode)")
        raise ValueError("Tài khoản email này chưa được đăng ký (Mock Mode)")

    web_api_key = os.getenv("FIREBASE_WEB_API_KEY")
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={web_api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload)
            data = response.json()
            if response.status_code != 200:
                error_msg = data.get("error", {}).get("message", "Đăng nhập thất bại")
                raise ValueError(error_msg)
            return {
                "id_token": data.get("idToken"),
                "refresh_token": data.get("refreshToken"),
                "uid": data.get("localId"),
                "email": data.get("email"),
                "display_name": data.get("displayName", "")
            }
    except httpx.RequestError as e:
        raise ValueError(f"Lỗi kết nối Firebase: {str(e)}")

def verify_firebase_token(id_token: str) -> dict:
    """Verify user ID Token (supporting mock tokens and official Firebase ID tokens)."""
    if id_token.startswith("mock_token_"):
        uid = id_token.replace("mock_token_", "")
        from modules.firebase_db import _load_mock_db
        mock_db = _load_mock_db()
        user = mock_db["users"].get(uid)
        if user:
            return {
                "uid": uid,
                "email": user["email"],
                "name": user.get("display_name", "")
            }
        raise ValueError("Không tìm thấy thông tin tài khoản thử nghiệm tương ứng")
        
    try:
        decoded_token = auth.verify_id_token(id_token)
        return {
            "uid": decoded_token.get("uid"),
            "email": decoded_token.get("email"),
            "name": decoded_token.get("name", "")
        }
    except Exception as e:
        raise ValueError(f"Xác thực token thất bại: {str(e)}")
