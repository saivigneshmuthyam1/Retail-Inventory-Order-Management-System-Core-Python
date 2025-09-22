# src/dao/product_dao.py
'''
from typing import Optional, List, Dict
from src.config import get_supabase
 
def _sb():
    return get_supabase()
 
def create_product(name: str, sku: str, price: float, stock: int = 0, category: str | None = None) -> Optional[Dict]:
    """
    Insert a product and return the inserted row (two-step: insert then select by unique sku).
    """
    payload = {"name": name, "sku": sku, "price": price, "stock": stock}
    if category is not None:
        payload["category"] = category
 
    # Insert (no select chaining)
    _sb().table("products").insert(payload).execute()
 
    # Fetch inserted row by unique column (sku)
    resp = _sb().table("products").select("*").eq("sku", sku).limit(1).execute()
    return resp.data[0] if resp.data else None
 
def get_product_by_id(prod_id: int) -> Optional[Dict]:
    resp = _sb().table("products").select("*").eq("prod_id", prod_id).limit(1).execute()
    return resp.data[0] if resp.data else None
 
def get_product_by_sku(sku: str) -> Optional[Dict]:
    resp = _sb().table("products").select("*").eq("sku", sku).limit(1).execute()
    return resp.data[0] if resp.data else None
 
def update_product(prod_id: int, fields: Dict) -> Optional[Dict]:
    """
    Update and then return the updated row (two-step).
    """
    _sb().table("products").update(fields).eq("prod_id", prod_id).execute()
    resp = _sb().table("products").select("*").eq("prod_id", prod_id).limit(1).execute()
    return resp.data[0] if resp.data else None
 
def delete_product(prod_id: int) -> Optional[Dict]:
    # fetch row before delete (so we can return it)
    resp_before = _sb().table("products").select("*").eq("prod_id", prod_id).limit(1).execute()
    row = resp_before.data[0] if resp_before.data else None
    _sb().table("products").delete().eq("prod_id", prod_id).execute()
    return row
 
def list_products(limit: int = 100, category: str | None = None) -> List[Dict]:
    q = _sb().table("products").select("*").order("prod_id", desc=False).limit(limit)
    if category:
        q = q.eq("category", category)
    resp = q.execute()
    return resp.data or []



# src/dao/product_dao.py
from typing import Optional, List, Dict
from supabase import Client

class ProductDAO:
    """
    Data Access Object for handling product-related database operations.
    """
    def __init__(self, db_client: Client):
        self.db = db_client
        self.table = "products"

    def create_product(self, name: str, sku: str, price: float, stock: int = 0, category: Optional[str] = None) -> Optional[Dict]:
        """
        Inserts a product and returns the inserted row by its unique SKU.
        """
        payload = {"name": name, "sku": sku, "price": price, "stock": stock}
        if category:
            payload["category"] = category

        # Insert and then fetch the new row
        self.db.table(self.table).insert(payload).execute()
        resp = self.db.table(self.table).select("*").eq("sku", sku).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_product_by_id(self, prod_id: int) -> Optional[Dict]:
        resp = self.db.table(self.table).select("*").eq("prod_id", prod_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_product_by_sku(self, sku: str) -> Optional[Dict]:
        resp = self.db.table(self.table).select("*").eq("sku", sku).limit(1).execute()
        return resp.data[0] if resp.data else None

    def update_product(self, prod_id: int, fields: Dict) -> Optional[Dict]:
        """
        Updates a product and returns the complete updated row.
        """
        self.db.table(self.table).update(fields).eq("prod_id", prod_id).execute()
        return self.get_product_by_id(prod_id)

    def delete_product(self, prod_id: int) -> Optional[Dict]:
        row = self.get_product_by_id(prod_id)
        if row:
            self.db.table(self.table).delete().eq("prod_id", prod_id).execute()
        return row

    def list_products(self, limit: int = 100, category: Optional[str] = None) -> List[Dict]:
        query = self.db.table(self.table).select("*").order("prod_id", desc=False).limit(limit)
        if category:
            query = query.eq("category", category)
        resp = query.execute()
        return resp.data or []
    
'''

# src/dao/product_dao.py
from typing import Optional, List, Dict
from supabase import Client

class ProductDAO:
    """
    Data Access Object for handling product-related database operations.
    """
    def __init__(self, db_client: Client):
        self.db = db_client
        self.table = "products"

    def create_product(self, name: str, sku: str, price: float, stock: int = 0, category: Optional[str] = None) -> Optional[Dict]:
        payload = {"name": name, "sku": sku, "price": price, "stock": stock, "category": category}
        self.db.table(self.table).insert(payload).execute()
        resp = self.db.table(self.table).select("*").eq("sku", sku).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_product_by_id(self, prod_id: int) -> Optional[Dict]:
        resp = self.db.table(self.table).select("*").eq("prod_id", prod_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_product_by_sku(self, sku: str) -> Optional[Dict]:
        resp = self.db.table(self.table).select("*").eq("sku", sku).limit(1).execute()
        return resp.data[0] if resp.data else None

    def update_product(self, prod_id: int, fields: Dict) -> Optional[Dict]:
        self.db.table(self.table).update(fields).eq("prod_id", prod_id).execute()
        return self.get_product_by_id(prod_id)

    def list_products(self, limit: int = 100) -> List[Dict]:
        resp = self.db.table(self.table).select("*").order("prod_id", desc=False).limit(limit).execute()
        return resp.data or []