# src/services/order_service.py
from typing import List, Dict
from src.dao.order_dao import OrderDAO
from src.dao.product_dao import ProductDAO
from src.dao.customer_dao import CustomerDAO
from src.dao.payment_dao import PaymentDAO # IMPORT PaymentDAO

class OrderError(Exception):
    pass

class OrderService:
    # UPDATE __init__ to accept payment_dao
    def __init__(self, order_dao: OrderDAO, product_dao: ProductDAO, customer_dao: CustomerDAO, payment_dao: PaymentDAO):
        self.order_dao = order_dao
        self.product_dao = product_dao
        self.customer_dao = customer_dao
        self.payment_dao = payment_dao # ADD this line

    def create_order(self, cust_id: int, items: List[Dict]) -> Dict:
        # ... (validation logic is the same) ...
        if not self.customer_dao.get_customer_by_id(cust_id):
            raise OrderError(f"Customer with ID {cust_id} not found.")
        total_amount = 0
        products_to_update = []
        for item in items:
            prod_id = item["prod_id"]
            quantity = item["quantity"]
            product = self.product_dao.get_product_by_id(prod_id)
            if not product:
                raise OrderError(f"Product with ID {prod_id} not found.")
            if product.get("stock", 0) < quantity:
                raise OrderError(f"Not enough stock for product '{product['name']}' (ID: {prod_id}). "
                                 f"Requested: {quantity}, Available: {product['stock']}.")
            item_price = product.get("price", 0)
            total_amount += item_price * quantity
            item["price"] = item_price
            products_to_update.append({"product": product, "quantity": quantity})
        
        new_order = self.order_dao.create_order(cust_id, total_amount)
        if not new_order:
            raise OrderError("Failed to create order record.")
        order_id = new_order["order_id"]

        # ADD THIS STEP: Create a pending payment record
        self.payment_dao.create_payment(order_id, total_amount)
        
        self.order_dao.create_order_items(order_id, items)
        for p_info in products_to_update:
            product = p_info["product"]
            new_stock = product["stock"] - p_info["quantity"]
            self.product_dao.update_product(product["prod_id"], {"stock": new_stock})
            
        return self.get_order_details(order_id)

    # ... (get_order_details and list_orders_for_customer are the same) ...
    def get_order_details(self, order_id: int) -> Dict:
        order = self.order_dao.get_order_by_id(order_id)
        if not order:
            raise OrderError(f"Order with ID {order_id} not found.")
        customer = self.customer_dao.get_customer_by_id(order["cust_id"])
        items = self.order_dao.get_order_items_by_order_id(order_id)
        order["customer"] = customer
        order["items"] = items
        return order

    def list_orders_for_customer(self, cust_id: int) -> List[Dict]:
        if not self.customer_dao.get_customer_by_id(cust_id):
            raise OrderError(f"Customer with ID {cust_id} not found.")
        return self.order_dao.list_orders_by_customer(cust_id)


    def cancel_order(self, order_id: int) -> Dict:
        order = self.order_dao.get_order_by_id(order_id)
        if not order:
            raise OrderError(f"Order with ID {order_id} not found.")
        if order["status"] != "PLACED":
            raise OrderError(f"Cannot cancel order. Status is '{order['status']}'.")

        # Restore stock logic is the same
        items = self.order_dao.get_order_items_by_order_id(order_id)
        for item in items:
            product = self.product_dao.get_product_by_id(item["prod_id"])
            if product:
                new_stock = product.get("stock", 0) + item["quantity"]
                self.product_dao.update_product(product["prod_id"], {"stock": new_stock})
        
        # ADD THIS STEP: Mark the payment as REFUNDED
        self.payment_dao.update_payment_by_order_id(order_id, {"status": "REFUNDED"})

        return self.order_dao.update_order_status(order_id, "CANCELLED")

    # The original complete_order is now handled by PaymentService
    # We can remove it or leave it as a manual override
    def complete_order(self, order_id: int) -> Dict:
        # This function is now superseded by process_payment, but can be kept for manual override
        return self.order_dao.update_order_status(order_id, "COMPLETED")