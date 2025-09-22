# src/services/product_service.py
'''
from typing import List, Dict
import src.dao.product_dao as product_dao
 
class ProductError(Exception):
    pass
 
def add_product(name: str, sku: str, price: float, stock: int = 0, category: str | None = None) -> Dict:
    """
    Validate and insert a new product.
    Raises ProductError on validation failure.
    """
    if price <= 0:
        raise ProductError("Price must be greater than 0")
    existing = product_dao.get_product_by_sku(sku)
    if existing:
        raise ProductError(f"SKU already exists: {sku}")
    return product_dao.create_product(name, sku, price, stock, category)
 
def restock_product(prod_id: int, delta: int) -> Dict:
    if delta <= 0:
        raise ProductError("Delta must be positive")
    p = product_dao.get_product_by_id(prod_id)
    if not p:
        raise ProductError("Product not found")
    new_stock = (p.get("stock") or 0) + delta
    return product_dao.update_product(prod_id, {"stock": new_stock})
 
def get_low_stock(threshold: int = 5) -> List[Dict]:
    allp = product_dao.list_products(limit=1000)
    return [p for p in allp if (p.get("stock") or 0) <= threshold]


# src/services/product_service.py
from typing import List, Dict, Optional
from src.dao.product_dao import ProductDAO

class ProductError(Exception):
    """Custom exception for product-related business logic errors."""
    pass

class ProductService:
    """
    Service class containing business logic for managing products.
    """
    def __init__(self, product_dao: ProductDAO):
        self.product_dao = product_dao

    def add_product(
        self,
        name: str,
        sku: str,
        price: float,
        stock: int = 0,
        category: Optional[str] = None
    ) -> Dict:
        """
        Validates and adds a new product.
        """
        if price <= 0:
            raise ProductError("Price must be a positive number.")
        
        if self.product_dao.get_product_by_sku(sku):
            raise ProductError(f"Product with SKU '{sku}' already exists.")

        return self.product_dao.create_product(name, sku, price, stock, category)

    def restock_product(self, prod_id: int, delta: int) -> Dict:
        """
        Increases the stock of an existing product.
        """
        if delta <= 0:
            raise ProductError("Restock quantity (delta) must be positive.")

        product = self.product_dao.get_product_by_id(prod_id)
        if not product:
            raise ProductError(f"Product with ID {prod_id} not found.")

        new_stock = (product.get("stock", 0) or 0) + delta
        return self.product_dao.update_product(prod_id, {"stock": new_stock})

    def get_low_stock(self, threshold: int = 5) -> List[Dict]:
        """
        Returns a list of products with stock at or below a given threshold.
        """
        all_products = self.product_dao.list_products(limit=1000)
        return [p for p in all_products if (p.get("stock", 0) or 0) <= threshold]

'''

# src/services/product_service.py
from typing import List, Dict, Optional
from src.dao.product_dao import ProductDAO

class ProductError(Exception):
    """Custom exception for product-related business logic errors."""
    pass

class ProductService:
    """
    Service class containing business logic for managing products.
    """
    def __init__(self, product_dao: ProductDAO):
        self.product_dao = product_dao

    def add_product(
        self, name: str, sku: str, price: float, stock: int = 0, category: Optional[str] = None
    ) -> Dict:
        """ Validates and adds a new product. """
        if price <= 0:
            raise ProductError("Price must be a positive number.")
        if self.product_dao.get_product_by_sku(sku):
            raise ProductError(f"Product with SKU '{sku}' already exists.")
        return self.product_dao.create_product(name, sku, price, stock, category)