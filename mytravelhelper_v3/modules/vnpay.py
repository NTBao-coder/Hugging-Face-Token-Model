import hmac
import hashlib
import urllib.parse
from typing import Dict, Any

class VNPay:
    """Helper class to integrate VNPAY payment gateway Sandbox (v2.1.0 API)."""
    
    def __init__(self, tmn_code: str, hash_secret: str, payment_url: str, return_url: str):
        self.tmn_code = tmn_code
        self.hash_secret = hash_secret
        self.payment_url = payment_url
        self.return_url = return_url

    def get_payment_url(self, order_id: str, amount: float, ip_addr: str, order_desc: str, create_date: str) -> str:
        """Generate redirection payment gateway URL."""
        vnp_params = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": self.tmn_code,
            "vnp_Amount": str(int(amount * 100)), # amount * 100 per VNPAY requirements
            "vnp_CreateDate": create_date,
            "vnp_CurrCode": "VND",
            "vnp_IpAddr": ip_addr,
            "vnp_Locale": "vn",
            "vnp_OrderInfo": order_desc,
            "vnp_OrderType": "other",
            "vnp_ReturnUrl": self.return_url,
            "vnp_TxnRef": order_id,
        }
        
        # Sort keys alphabetically
        sorted_params = sorted(vnp_params.items())
        
        # Construct the query string
        hash_data = []
        for key, val in sorted_params:
            hash_data.append(f"{key}={urllib.parse.quote_plus(str(val))}")
        hash_string = "&".join(hash_data)
        
        # Compute HMAC-SHA512
        secure_hash = hmac.new(
            self.hash_secret.encode("utf-8"),
            hash_string.encode("utf-8"),
            hashlib.sha512
        ).hexdigest()
        
        # Append SecureHash to redirection params
        redirect_params = []
        for key, val in sorted_params:
            redirect_params.append(f"{key}={urllib.parse.quote_plus(str(val))}")
        redirect_params.append(f"vnp_SecureHash={secure_hash}")
        
        return f"{self.payment_url}?{'&'.join(redirect_params)}"

    def validate_response(self, response_params: Dict[str, Any]) -> bool:
        """Verify secure hash from response returned by VNPAY."""
        if "vnp_SecureHash" not in response_params:
            return False
        
        secure_hash = response_params["vnp_SecureHash"]
        
        # Extract and sort vnp_ parameters, excluding hash and hash type
        vnp_data = {}
        for key, val in response_params.items():
            if key.startswith("vnp_") and key != "vnp_SecureHash" and key != "vnp_SecureHashType":
                # Ensure it's a string value
                if isinstance(val, list):
                    vnp_data[key] = val[0]
                else:
                    vnp_data[key] = val
                    
        sorted_params = sorted(vnp_data.items())
        
        # Build query string
        hash_data = []
        for key, val in sorted_params:
            hash_data.append(f"{key}={urllib.parse.quote_plus(str(val))}")
        hash_string = "&".join(hash_data)
        
        # Compute HMAC-SHA512 checksum
        calculated_hash = hmac.new(
            self.hash_secret.encode("utf-8"),
            hash_string.encode("utf-8"),
            hashlib.sha512
        ).hexdigest()
        
        return calculated_hash.lower() == secure_hash.lower()
