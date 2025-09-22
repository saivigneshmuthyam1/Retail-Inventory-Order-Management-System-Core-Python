# src/services/reporting_service.py
from typing import Dict
from src.dao.order_dao import OrderDAO

class ReportingService:
    """
    Service for generating business reports.
    """
    def __init__(self, order_dao: OrderDAO):
        self.order_dao = order_dao

    def generate_sales_summary(self, start_date: str, end_date: str) -> Dict:
        """
        Generates a sales summary report for a given date range.
        """
        report_data = self.order_dao.get_sales_report_data(start_date, end_date)
        
        # The DAO returns a list with one object, or an empty list
        if not report_data:
            summary = {"total_revenue": 0, "total_orders": 0}
        else:
            summary = report_data[0]

        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_revenue": summary.get("total_revenue") or 0,
            "total_orders": summary.get("total_orders") or 0
        }