# src/dao/order_dao.py
from typing import List, Dict, Optional
from supabase import Client

class OrderDAO:
    """
    Data Access Object for order-related database operations.
    """
    def __init__(self, db_client: Client):
        self.db = db_client

    def create_order(self, cust_id: int, total_amount: float, status: str = "PLACED") -> Optional[Dict]:
        """Inserts a new order record and returns it."""
        payload = {"cust_id": cust_id, "total_amount": total_amount, "status": status}
        resp = self.db.table("orders").insert(payload).execute()
        return resp.data[0] if resp.data else None

    def create_order_items(self, order_id: int, items: List[Dict]) -> List[Dict]:
        """
        Inserts multiple item records for a given order.
        """
        payload = [
            {"order_id": order_id, "prod_id": item["prod_id"], "quantity": item["quantity"], "price": item["price"]}
            for item in items
        ]
        resp = self.db.table("order_items").insert(payload).execute()
        return resp.data or []

    def get_order_by_id(self, order_id: int) -> Optional[Dict]:
        """Retrieves a single order by its ID."""
        resp = self.db.table("orders").select("*").eq("order_id", order_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_order_items_by_order_id(self, order_id: int) -> List[Dict]:
        """Retrieves all items associated with a single order."""
        resp = self.db.table("order_items").select("*, products(name, sku)").eq("order_id", order_id).execute()
        return resp.data or []
        
    def list_orders_by_customer(self, cust_id: int) -> List[Dict]:
        """Retrieves all orders placed by a specific customer."""
        resp = self.db.table("orders").select("*").eq("cust_id", cust_id).order("order_date", desc=True).execute()
        return resp.data or []

    def update_order_status(self, order_id: int, status: str) -> Optional[Dict]:
        """Updates the status of an order."""
        resp = self.db.table("orders").update({"status": status}).eq("order_id", order_id).execute()
        return resp.data[0] if resp.data else None
    
    # ADD THIS NEW METHOD FOR REPORTING
    def get_sales_report_data(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Fetches aggregated sales data for completed orders within a date range
        by calling a PostgreSQL function (RPC).
        """
        resp = self.db.rpc('sales_report', {'start_date': start_date, 'end_date': end_date}).execute()
        return resp.data or []