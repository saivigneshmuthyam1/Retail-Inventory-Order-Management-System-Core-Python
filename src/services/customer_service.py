# src/services/customer_service.py
from typing import Optional, List, Dict
from src.dao.customer_dao import CustomerDAO
from src.dao.order_dao import OrderDAO

class CustomerError(Exception):
    """Custom exception for customer-related business logic errors."""
    pass

class CustomerService:
    def __init__(self, customer_dao: CustomerDAO, order_dao: OrderDAO):
        self.customer_dao = customer_dao
        self.order_dao = order_dao

    def add_customer(self, name: str, email: str, phone: str, city: Optional[str]) -> Dict:
        if self.customer_dao.get_customer_by_email(email):
            raise CustomerError(f"A customer with email '{email}' already exists.")
        return self.customer_dao.create_customer(name, email, phone, city)

    def update_customer_details(self, cust_id: int, phone: Optional[str] = None, city: Optional[str] = None) -> Dict:
        if not phone and not city:
            raise CustomerError("No update information provided. Please supply a phone or city.")
        if not self.customer_dao.get_customer_by_id(cust_id):
            raise CustomerError(f"Customer with ID {cust_id} not found.")
        fields_to_update = {k: v for k, v in {"phone": phone, "city": city}.items() if v is not None}
        return self.customer_dao.update_customer(cust_id, fields_to_update)

    def delete_customer(self, cust_id: int) -> Dict:
        if not self.customer_dao.get_customer_by_id(cust_id):
            raise CustomerError(f"Customer with ID {cust_id} not found.")
        orders = self.order_dao.list_orders_by_customer(cust_id)
        if orders:
            raise CustomerError(f"Cannot delete customer {cust_id}. They have {len(orders)} existing order(s).")
        return self.customer_dao.delete_customer(cust_id)

    def list_all_customers(self) -> List[Dict]:
        return self.customer_dao.list_customers()

    def find_customer(self, email: Optional[str] = None, city: Optional[str] = None) -> List[Dict]:
        if not email and not city:
            raise CustomerError("Please provide an email or a city to search by.")
        if email:
            customer = self.customer_dao.get_customer_by_email(email)
            return [customer] if customer else []
        if city:
            return self.customer_dao.search_customers_by_city(city)
        return []