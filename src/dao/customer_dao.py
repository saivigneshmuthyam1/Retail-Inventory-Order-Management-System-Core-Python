# src/dao/customer_dao.py
from typing import Optional, List, Dict
from supabase import Client

class CustomerDAO:
    """
    Data Access Object for handling customer-related database operations.
    """
    def __init__(self, db_client: Client):
        self.db = db_client
        self.table = "customers"

    def create_customer(self, name: str, email: str, phone: str, city: Optional[str]) -> Optional[Dict]:
        resp = self.db.table(self.table).insert({"name": name, "email": email, "phone": phone, "city": city}).execute()
        return resp.data[0] if resp.data else None

    def get_customer_by_email(self, email: str) -> Optional[Dict]:
        resp = self.db.table(self.table).select("*").eq("email", email).limit(1).execute()
        return resp.data[0] if resp.data else None
    
    def get_customer_by_id(self, cust_id: int) -> Optional[Dict]:
        resp = self.db.table(self.table).select("*").eq("cust_id", cust_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def update_customer(self, cust_id: int, fields: Dict) -> Optional[Dict]:
        resp = self.db.table(self.table).update(fields).eq("cust_id", cust_id).execute()
        return resp.data[0] if resp.data else None

    def delete_customer(self, cust_id: int) -> Optional[Dict]:
        resp = self.db.table(self.table).delete().eq("cust_id", cust_id).execute()
        return resp.data[0] if resp.data else None

    def list_customers(self, limit: int = 100) -> List[Dict]:
        resp = self.db.table(self.table).select("*").order("cust_id").limit(limit).execute()
        return resp.data or []

    def search_customers_by_city(self, city: str, limit: int = 100) -> List[Dict]:
        resp = self.db.table(self.table).select("*").eq("city", city).limit(limit).execute()
        return resp.data or []