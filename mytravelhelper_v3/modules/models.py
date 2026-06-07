from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Mật khẩu tối thiểu 6 ký tự")
    display_name: str = Field(..., min_length=2, description="Tên hiển thị người dùng")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenVerify(BaseModel):
    id_token: str

class OrderCreate(BaseModel):
    service_type: str  # "hotel_booking" | "tour" | "flight"
    service_name: str
    amount: float      # Số tiền dạng VND

class PaymentCreate(BaseModel):
    order_id: str
    ip_address: str

class PaymentInfo(BaseModel):
    vnpay_transaction_no: str
    bank_code: str
    pay_date: str
    response_code: str
    secure_hash_verified: bool

class OrderResponse(BaseModel):
    order_id: str
    uid: str
    service_type: str
    service_name: str
    amount: float
    status: str
    created_at: datetime
    updated_at: datetime
    vnpay_txn_ref: str
    payment_info: Optional[Dict[str, Any]] = None
