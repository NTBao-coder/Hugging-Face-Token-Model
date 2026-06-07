import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import json

# Thread-safe global client cache
_db_client = None

def get_db():
    """Retrieve Firestore client dynamically to handle import order variations."""
    global _db_client
    if _db_client is None:
        try:
            import firebase_admin
            from firebase_admin import firestore
            if firebase_admin._apps:
                _db_client = firestore.client()
        except Exception as e:
            # Silent warning to prevent terminal spamming during offline dev
            pass
    return _db_client

# Local Mock Database File for Offline Mode
MODULE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_DIR.parent
MOCK_DB_PATH = PROJECT_ROOT / "data" / "mock_database.json"

def _load_mock_db() -> Dict[str, Any]:
    """Helper to read mock database file."""
    if not MOCK_DB_PATH.parent.exists():
        MOCK_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if MOCK_DB_PATH.exists():
        try:
            with open(MOCK_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"users": {}, "orders": {}, "transactions": {}}

def _save_mock_db(data: Dict[str, Any]):
    """Helper to write to mock database file."""
    try:
        with open(MOCK_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, default=str, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Failed to save mock database: {e}")

def create_user_profile(uid: str, email: str, display_name: str) -> bool:
    """Save user profile to users collection."""
    user_data = {
        "uid": uid,
        "email": email,
        "display_name": display_name,
        "created_at": datetime.now(),
        "total_spent": 0.0
    }
    
    firestore_db = get_db()
    if firestore_db is not None:
        try:
            firestore_db.collection("users").document(uid).set(user_data)
            return True
        except Exception as e:
            print(f"Firestore error in create_user_profile: {e}")
            
    # Mock fallback
    mock_db = _load_mock_db()
    # CRITICAL BUG FIX: Preserve the password of the mock user
    existing_user = mock_db["users"].get(uid, {})
    if "password" in existing_user:
        user_data["password"] = existing_user["password"]
    else:
        # Fallback default password in case it was created elsewhere
        user_data["password"] = "123456"
        
    mock_db["users"][uid] = user_data
    _save_mock_db(mock_db)
    return True

def create_order(order_id: str, uid: str, service_type: str, service_name: str, amount: float) -> bool:
    """Create a new order in orders collection with pending status."""
    now = datetime.now()
    order_data = {
        "order_id": order_id,
        "uid": uid,
        "service_type": service_type,
        "service_name": service_name,
        "amount": amount,
        "status": "pending",
        "created_at": now,
        "updated_at": now,
        "vnpay_txn_ref": order_id,
        "payment_info": None
    }
    
    firestore_db = get_db()
    if firestore_db is not None:
        try:
            firestore_db.collection("orders").document(order_id).set(order_data)
            return True
        except Exception as e:
            print(f"Firestore error in create_order: {e}")
            
    # Mock fallback
    mock_db = _load_mock_db()
    mock_db["orders"][order_id] = order_data
    _save_mock_db(mock_db)
    return True

def get_order(order_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve order details by order_id."""
    firestore_db = get_db()
    if firestore_db is not None:
        try:
            doc = firestore_db.collection("orders").document(order_id).get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            print(f"Firestore error in get_order: {e}")
            
    # Mock fallback
    mock_db = _load_mock_db()
    return mock_db["orders"].get(order_id)

def update_order_status(order_id: str, status: str, payment_info: Optional[Dict[str, Any]] = None) -> bool:
    """Update order status and optionally set payment_info."""
    update_data = {
        "status": status,
        "updated_at": datetime.now()
    }
    if payment_info is not None:
        update_data["payment_info"] = payment_info
        
    firestore_db = get_db()
    if firestore_db is not None:
        try:
            firestore_db.collection("orders").document(order_id).update(update_data)
            return True
        except Exception as e:
            print(f"Firestore error in update_order_status: {e}")
            
    # Mock fallback
    mock_db = _load_mock_db()
    if order_id in mock_db["orders"]:
        mock_db["orders"][order_id].update(update_data)
        
        # Update user total spent if paid
        if status == "paid":
            order = mock_db["orders"][order_id]
            uid = order.get("uid")
            amount = order.get("amount", 0.0)
            if uid in mock_db["users"]:
                spent = mock_db["users"][uid].get("total_spent", 0.0)
                mock_db["users"][uid]["total_spent"] = spent + amount
                
        _save_mock_db(mock_db)
        return True
    return False

def log_transaction(txn_id: str, order_id: str, uid: str, amount: float, txn_type: str, raw_data: Dict[str, Any], verified: bool) -> bool:
    """Log VNPAY transaction logs."""
    txn_data = {
        "txn_id": txn_id,
        "order_id": order_id,
        "uid": uid,
        "amount": amount,
        "type": txn_type, # "ipn" or "return"
        "raw_data": raw_data,
        "verified": verified,
        "created_at": datetime.now()
    }
    
    firestore_db = get_db()
    if firestore_db is not None:
        try:
            firestore_db.collection("transactions").document(txn_id).set(txn_data)
            return True
        except Exception as e:
            print(f"Firestore error in log_transaction: {e}")
            
    # Mock fallback
    mock_db = _load_mock_db()
    mock_db["transactions"][txn_id] = txn_data
    _save_mock_db(mock_db)
    return True

def get_user_orders(uid: str) -> List[Dict[str, Any]]:
    """Retrieve list of orders belonging to a specific user ID."""
    firestore_db = get_db()
    if firestore_db is not None:
        try:
            docs = firestore_db.collection("orders").where("uid", "==", uid).order_by("created_at", direction=firestore.Query.DESCENDING).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f"Firestore error in get_user_orders: {e}. Checking without order_by index...")
            try:
                # Fallback in case firestore index isn't built yet
                docs = firestore_db.collection("orders").where("uid", "==", uid).stream()
                orders = [doc.to_dict() for doc in docs]
                orders.sort(key=lambda x: x.get("created_at"), reverse=True)
                return orders
            except Exception as ex:
                print(f"Firestore query failed entirely: {ex}")
                
    # Mock fallback
    mock_db = _load_mock_db()
    user_orders = []
    for order in mock_db["orders"].values():
        if order.get("uid") == uid:
            user_orders.append(order)
    user_orders.sort(key=lambda x: x.get("created_at"), reverse=True)
    return user_orders
