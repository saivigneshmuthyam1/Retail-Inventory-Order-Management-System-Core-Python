# src/dao/payment_dao.py
from typing import Dict, Optional
from supabase import Client
import datetime

class PaymentDAO:
    """
    Data Access Object for handling payment-related database operations.
    """
    def __init__(self, db_client: Client):
        self.db = db_client
        self.table = "payments"

    def create_payment(self, order_id: int, amount: float, status: str = "PENDING") -> Optional[Dict]:
        """Inserts a new payment record."""
        payload = {"order_id": order_id, "amount": amount, "status": status}
        resp = self.db.table(self.table).insert(payload).execute()
        return resp.data[0] if resp.data else None

    def get_payment_by_order_id(self, order_id: int) -> Optional[Dict]:
        """Retrieves a payment record by its associated order_id."""
        resp = self.db.table(self.table).select("*").eq("order_id", order_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def update_payment_by_order_id(self, order_id: int, updates: Dict) -> Optional[Dict]:
        """
        Updates a payment record using the order_id.
        Automatically adds the 'paid_at' timestamp if status is 'PAID'.
        """
        if updates.get("status") == "PAID":
            updates["paid_at"] = datetime.datetime.now().isoformat()
            
        resp = self.db.table(self.table).update(updates).eq("order_id", order_id).execute()
        return resp.data[0] if resp.data else None