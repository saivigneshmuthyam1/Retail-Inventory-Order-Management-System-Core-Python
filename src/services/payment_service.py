# src/services/payment_service.py
from typing import Dict
from src.dao.payment_dao import PaymentDAO
from src.dao.order_dao import OrderDAO

class PaymentError(Exception):
    """Custom exception for payment-related errors."""
    pass

class PaymentService:
    """
    Service class containing business logic for processing payments.
    """
    def __init__(self, payment_dao: PaymentDAO, order_dao: OrderDAO):
        self.payment_dao = payment_dao
        self.order_dao = order_dao

    def process_payment(self, order_id: int, method: str) -> Dict:
        """
        Processes a payment for an order and updates the order status.
        """
        payment = self.payment_dao.get_payment_by_order_id(order_id)
        if not payment:
            raise PaymentError(f"No pending payment found for order ID {order_id}.")
        if payment["status"] != "PENDING":
            raise PaymentError(f"Payment for order ID {order_id} is not pending (status: {payment['status']}).")

        # Update payment status
        updates = {"status": "PAID", "method": method}
        updated_payment = self.payment_dao.update_payment_by_order_id(order_id, updates)

        # Update order status to COMPLETED
        self.order_dao.update_order_status(order_id, "COMPLETED")

        return updated_payment