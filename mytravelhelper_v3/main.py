import os
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

from modules.models import (
    UserRegister,
    UserLogin,
    TokenVerify,
    OrderCreate,
    OrderResponse,
    PaymentCreate
)
from modules.firebase_auth import (
    register_user,
    login_user,
    verify_firebase_token,
    init_firebase
)
from modules.firebase_db import (
    create_user_profile,
    create_order,
    get_order,
    update_order_status,
    log_transaction,
    get_user_orders
)
from modules.vnpay import VNPay

# Load environment variables
load_dotenv()

# Initialize Firebase Admin
init_firebase()

# Initialize FastAPI App
app = FastAPI(
    title="MyTravelHelper — VNPAY Payment Backend",
    description="FastAPI Backend for User Authentication, Ordering, and VNPAY Sandbox Integration",
    version="3.0.0"
)

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize VNPAY client
vnpay_client = VNPay(
    tmn_code=os.getenv("VNPAY_TMN_CODE", "DEMO_TMN"),
    hash_secret=os.getenv("VNPAY_HASH_SECRET", "DEMO_SECRET"),
    payment_url=os.getenv("VNPAY_URL", "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"),
    return_url=os.getenv("VNPAY_RETURN_URL", "http://localhost:8000/api/payment/return")
)

# Authentication Security Dependency
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Validate Bearer Firebase ID Token."""
    token = credentials.credentials
    try:
        user_info = verify_firebase_token(token)
        return user_info
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

# ----------------- API ENDPOINTS -----------------

@app.get("/api/health")
def health_check():
    """Simple status check for backend and config."""
    return {
        "status": "healthy",
        "time": datetime.now().isoformat(),
        "vnpay_configured": os.getenv("VNPAY_TMN_CODE") is not None,
        "firebase_configured": os.getenv("FIREBASE_WEB_API_KEY") is not None
    }

@app.get("/api/services")
def api_get_services():
    """Retrieve list of all active travel services/destinations."""
    import json
    from pathlib import Path
    services_path = Path(__file__).resolve().parent / "config" / "services.json"
    if not services_path.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy cấu hình dịch vụ")
    try:
        with open(services_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi đọc dữ liệu: {e}")

@app.post("/api/auth/register")
def auth_register(payload: UserRegister):
    """Register user in Firebase Auth and Firestore profile."""
    try:
        user_info = register_user(payload.email, payload.password, payload.display_name)
        create_user_profile(user_info["uid"], user_info["email"], user_info["display_name"])
        return {
            "success": True,
            "message": "Đăng ký tài khoản thành công",
            "user": user_info
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.post("/api/auth/login")
def auth_login(payload: UserLogin):
    """Log in user and return Firebase tokens."""
    try:
        login_data = login_user(payload.email, payload.password)
        return login_data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@app.post("/api/auth/verify")
def auth_verify(payload: TokenVerify):
    """Verify Firebase ID Token."""
    try:
        user_info = verify_firebase_token(payload.id_token)
        return {
            "valid": True,
            "user": user_info
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@app.post("/api/orders/create", response_model=OrderResponse)
def api_create_order(payload: OrderCreate, current_user: dict = Depends(get_current_user)):
    """Create a new pending order in database."""
    order_id = f"DH{datetime.now():%Y%m%d%H%M%S}{random.randint(1000, 9999)}"
    
    success = create_order(
        order_id=order_id,
        uid=current_user["uid"],
        service_type=payload.service_type,
        service_name=payload.service_name,
        amount=payload.amount
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Không thể lưu trữ đơn hàng"
        )
        
    order = get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đơn hàng sau khi tạo"
        )
    return order

@app.get("/api/orders/history", response_model=List[OrderResponse])
def api_order_history(current_user: dict = Depends(get_current_user)):
    """Retrieve all orders of the logged-in user."""
    orders = get_user_orders(current_user["uid"])
    return orders

@app.get("/api/orders/{order_id}", response_model=OrderResponse)
def api_get_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """Fetch specific order details."""
    order = get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    
    # Authorize user owns the order
    if order["uid"] != current_user["uid"]:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem đơn hàng này")
        
    return order

@app.post("/api/payment/create-url")
def api_create_payment_url(payload: PaymentCreate, current_user: dict = Depends(get_current_user)):
    """Generate VNPAY payment gateway URL for a pending order."""
    order = get_order(payload.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
        
    if order["uid"] != current_user["uid"]:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập đơn hàng này")
        
    if order["status"] != "pending":
        raise HTTPException(status_code=400, detail="Đơn hàng này đã được thanh toán hoặc đã hủy")
        
    create_date = datetime.now().strftime("%Y%m%d%H%M%S")
    payment_url = vnpay_client.get_payment_url(
        order_id=payload.order_id,
        amount=order["amount"],
        ip_addr=payload.ip_address,
        order_desc=f"Thanh toan don hang {payload.order_id}",
        create_date=create_date
    )
    
    return {
        "payment_url": payment_url,
        "order_id": payload.order_id,
        "amount": order["amount"]
    }

@app.get("/api/payment/return")
def api_payment_return(request: Request):
    """VNPAY redirection callback return URL. Verifies checksum and redirects to Streamlit."""
    params = dict(request.query_params)
    
    # 1. Validate signature
    hash_valid = vnpay_client.validate_response(params)
    
    order_id = params.get("vnp_TxnRef")
    response_code = params.get("vnp_ResponseCode", "99")
    amount_raw = params.get("vnp_Amount")
    txn_no = params.get("vnp_TransactionNo", "")
    bank_code = params.get("vnp_BankCode", "")
    pay_date = params.get("vnp_PayDate", "")
    
    # Resolve user id
    uid = "unknown"
    amount = 0.0
    if order_id:
        order = get_order(order_id)
        if order:
            uid = order.get("uid", "unknown")
            amount = order.get("amount", 0.0)
            
    # Calculate amount from response
    if amount_raw:
        try:
            amount = float(amount_raw) / 100
        except ValueError:
            pass
            
    # 2. Log transaction and update order status for local testing fallback
    if txn_no:
        log_transaction(
            txn_id=f"RET_{txn_no}",
            order_id=order_id,
            uid=uid,
            amount=amount,
            txn_type="return",
            raw_data=params,
            verified=hash_valid
        )

    # If signature is valid, update the order status in database as a fallback for local testing
    if hash_valid and order_id:
        order = get_order(order_id)
        if order and order.get("status") == "pending":
            status_to_set = "paid" if response_code == "00" else "failed"
            payment_info = {
                "vnpay_transaction_no": txn_no,
                "bank_code": bank_code,
                "pay_date": pay_date,
                "response_code": response_code,
                "secure_hash_verified": True,
                "updated_by": "return_callback_fallback"
            }
            update_order_status(order_id, status=status_to_set, payment_info=payment_info)
        
    # Redirect URL
    frontend_base = os.getenv("FRONTEND_URL", "http://localhost:8501")
    if "5173" in frontend_base or "3000" in frontend_base:
        # React frontend
        redirect_target = frontend_base.rstrip("/")
    else:
        # Streamlit frontend
        redirect_target = f"{frontend_base.rstrip('/')}/Payment"
    
    # Rebuild query parameters
    query_string = request.url.query
    final_redirect_url = f"{redirect_target}?{query_string}"
    
    return RedirectResponse(url=final_redirect_url)

@app.api_route("/api/payment/ipn", methods=["GET", "POST"])
async def api_payment_ipn(request: Request):
    """VNPAY Server-to-Server Instant Payment Notification webhook."""
    # 1. Fetch parameters from request
    params = dict(request.query_params)
    
    if not params:
        # Try retrieving from form parameters or json
        try:
            params = await request.json()
        except Exception:
            try:
                form_data = await request.form()
                params = dict(form_data)
            except Exception:
                pass
                
    # If still empty
    if not params:
        return {"RspCode": "99", "Message": "No parameters received"}
        
    order_id = params.get("vnp_TxnRef")
    response_code = params.get("vnp_ResponseCode")
    amount_raw = params.get("vnp_Amount")
    txn_no = params.get("vnp_TransactionNo", "")
    bank_code = params.get("vnp_BankCode", "")
    pay_date = params.get("vnp_PayDate", "")
    
    # 2. Validate Checksum Signature
    hash_valid = vnpay_client.validate_response(params)
    if not hash_valid:
        return {"RspCode": "97", "Message": "Invalid Signature"}
        
    # 3. Check Order Existence
    if not order_id:
        return {"RspCode": "01", "Message": "Order Not Found (Missing ID)"}
        
    order = get_order(order_id)
    if not order:
        return {"RspCode": "01", "Message": "Order Not Found"}
        
    # 4. Check Amount Validity
    if amount_raw:
        try:
            vnp_amount = float(amount_raw) / 100
            if vnp_amount != order["amount"]:
                return {"RspCode": "04", "Message": "Invalid Amount"}
        except ValueError:
            return {"RspCode": "04", "Message": "Invalid Amount format"}
            
    # 5. Check Idempotency (Already confirmed)
    if order["status"] != "pending":
        return {"RspCode": "02", "Message": "Order already confirmed"}
        
    # 6. Process payment status
    status_to_set = "paid" if response_code == "00" else "failed"
    
    payment_info = {
        "vnpay_transaction_no": txn_no,
        "bank_code": bank_code,
        "pay_date": pay_date,
        "response_code": response_code,
        "secure_hash_verified": True
    }
    
    # Update order in DB
    update_order_status(order_id, status=status_to_set, payment_info=payment_info)
    
    # Log webhook transaction
    if txn_no:
        log_transaction(
            txn_id=f"IPN_{txn_no}",
            order_id=order_id,
            uid=order["uid"],
            amount=order["amount"],
            txn_type="ipn",
            raw_data=params,
            verified=True
        )
        
    return {"RspCode": "00", "Message": "Confirm Success"}
