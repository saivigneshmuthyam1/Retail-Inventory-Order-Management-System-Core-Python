# src/cli/main.py
import argparse
import json
from src.config import config
from src.dao.product_dao import ProductDAO
from src.dao.customer_dao import CustomerDAO
from src.dao.order_dao import OrderDAO
from src.dao.payment_dao import PaymentDAO
from src.services.product_service import ProductService, ProductError
from src.services.customer_service import CustomerService, CustomerError
from src.services.order_service import OrderService, OrderError
from src.services.payment_service import PaymentService, PaymentError
from src.services.reporting_service import ReportingService

class RetailCLI:
    def __init__(self):
        db_client = config.get_supabase_client()
        # DAOs
        product_dao = ProductDAO(db_client)
        customer_dao = CustomerDAO(db_client)
        order_dao = OrderDAO(db_client)
        payment_dao = PaymentDAO(db_client)
        # Services
        self.product_service = ProductService(product_dao)
        self.customer_service = CustomerService(customer_dao, order_dao)
        self.order_service = OrderService(order_dao, product_dao, customer_dao, payment_dao)
        self.payment_service = PaymentService(payment_dao, order_dao)
        self.reporting_service = ReportingService(order_dao)

    def run(self):
        parser = self._build_parser()
        args = parser.parse_args()
        if not hasattr(args, "func"):
            parser.print_help()
            return
        args.func(args)
        
    # --- Product Command Handlers ---
    def _cmd_product_add(self, args):
        try:
            p = self.product_service.add_product(args.name, args.sku, args.price, args.stock, args.category)
            print("✅ Product created successfully:")
            print(json.dumps(p, indent=2, default=str))
        except ProductError as e:
            print(f"❌ Error: {e}")

    def _cmd_product_list(self, args):
        products = self.product_service.product_dao.list_products(limit=100)
        print(json.dumps(products, indent=2, default=str))

    # --- Customer Command Handlers ---
    def _cmd_customer_add(self, args):
        try:
            c = self.customer_service.add_customer(args.name, args.email, args.phone, args.city)
            print("✅ Customer created successfully:")
            print(json.dumps(c, indent=2, default=str))
        except CustomerError as e:
            print(f"❌ Error: {e}")

    def _cmd_customer_update(self, args):
        try:
            c = self.customer_service.update_customer_details(args.id, args.phone, args.city)
            print(f"✅ Customer {args.id} updated successfully:")
            print(json.dumps(c, indent=2, default=str))
        except CustomerError as e:
            print(f"❌ Error: {e}")

    def _cmd_customer_delete(self, args):
        try:
            c = self.customer_service.delete_customer(args.id)
            print(f"✅ Customer {args.id} deleted successfully:")
            print(json.dumps(c, indent=2, default=str))
        except CustomerError as e:
            print(f"❌ Error: {e}")

    def _cmd_customer_list(self, args):
        customers = self.customer_service.list_all_customers()
        print(json.dumps(customers, indent=2, default=str))
    
    def _cmd_customer_search(self, args):
        try:
            customers = self.customer_service.find_customer(email=args.email, city=args.city)
            if not customers:
                print("No customers found matching the criteria.")
                return
            print(json.dumps(customers, indent=2, default=str))
        except CustomerError as e:
            print(f"❌ Error: {e}")

    # --- Order Command Handlers ---
    def _cmd_order_create(self, args):
        items = []
        for item_str in args.item:
            try:
                prod_id, qty = item_str.split(":")
                items.append({"prod_id": int(prod_id), "quantity": int(qty)})
            except ValueError:
                print(f"❌ Error: Invalid item format '{item_str}'. Use prod_id:qty.")
                return
        try:
            order = self.order_service.create_order(args.cust_id, items)
            print("✅ Order created successfully (payment pending):")
            print(json.dumps(order, indent=2, default=str))
        except OrderError as e:
            print(f"❌ Error: {e}")

    def _cmd_order_show(self, args):
        try:
            order = self.order_service.get_order_details(args.order_id)
            print(json.dumps(order, indent=2, default=str))
        except OrderError as e:
            print(f"❌ Error: {e}")

    def _cmd_order_list(self, args):
        try:
            orders = self.order_service.list_orders_for_customer(args.cust_id)
            print(json.dumps(orders, indent=2, default=str))
        except OrderError as e:
            print(f"❌ Error: {e}")

    def _cmd_order_cancel(self, args):
        try:
            order = self.order_service.cancel_order(args.order_id)
            print(f"✅ Order {args.order_id} cancelled and payment refunded:")
            print(json.dumps(order, indent=2, default=str))
        except OrderError as e:
            print(f"❌ Error: {e}")

    # --- Payment Command Handlers ---
    def _cmd_payment_process(self, args):
        try:
            payment = self.payment_service.process_payment(args.order_id, args.method)
            print(f"✅ Payment for order {args.order_id} processed successfully:")
            print(json.dumps(payment, indent=2, default=str))
        except PaymentError as e:
            print(f"❌ Error: {e}")

    # --- Reporting Command Handlers ---
    def _cmd_report_sales(self, args):
        try:
            summary = self.reporting_service.generate_sales_summary(args.start_date, args.end_date)
            print("📈 Sales Summary Report:")
            print(json.dumps(summary, indent=2, default=str))
        except Exception as e:
            print(f"❌ Error generating report: {e}")

    def _build_parser(self):
        parser = argparse.ArgumentParser(prog="retail-cli")
        sub = parser.add_subparsers(dest="cmd", help="Available commands")
        
        # Product commands
        p_prod = sub.add_parser("product", help="Manage products")
        pprod_sub = p_prod.add_subparsers(dest="action", required=True)
        addp = pprod_sub.add_parser("add", help="Add a new product")
        addp.add_argument("--name", required=True)
        addp.add_argument("--sku", required=True)
        addp.add_argument("--price", type=float, required=True)
        addp.add_argument("--stock", type=int, default=0)
        addp.add_argument("--category")
        addp.set_defaults(func=self._cmd_product_add)
        listp = pprod_sub.add_parser("list", help="List all products")
        listp.set_defaults(func=self._cmd_product_list)
        
        # Customer commands
        p_cust = sub.add_parser("customer", help="Manage customers")
        pcust_sub = p_cust.add_subparsers(dest="action", required=True)
        addc = pcust_sub.add_parser("add", help="Add a new customer")
        addc.add_argument("--name", required=True)
        addc.add_argument("--email", required=True)
        addc.add_argument("--phone", required=True)
        addc.add_argument("--city")
        addc.set_defaults(func=self._cmd_customer_add)
        updc = pcust_sub.add_parser("update", help="Update a customer's phone or city")
        updc.add_argument("--id", type=int, required=True, help="ID of the customer to update")
        updc.add_argument("--phone", help="New phone number")
        updc.add_argument("--city", help="New city")
        updc.set_defaults(func=self._cmd_customer_update)
        delc = pcust_sub.add_parser("delete", help="Delete a customer")
        delc.add_argument("--id", type=int, required=True, help="ID of the customer to delete")
        delc.set_defaults(func=self._cmd_customer_delete)
        listc = pcust_sub.add_parser("list", help="List all customers")
        listc.set_defaults(func=self._cmd_customer_list)
        searchc = pcust_sub.add_parser("search", help="Search for a customer by email or city")
        search_group = searchc.add_mutually_exclusive_group(required=True)
        search_group.add_argument("--email", help="Email to search for")
        search_group.add_argument("--city", help="City to search for")
        searchc.set_defaults(func=self._cmd_customer_search)

        # Order commands
        p_order = sub.add_parser("order", help="Manage orders")
        porder_sub = p_order.add_subparsers(dest="action", required=True)
        createo = porder_sub.add_parser("create", help="Create a new order")
        createo.add_argument("--cust-id", type=int, required=True)
        createo.add_argument("--item", required=True, nargs="+", help="Format: prod_id:qty")
        createo.set_defaults(func=self._cmd_order_create)
        showo = porder_sub.add_parser("show", help="Show details of a specific order")
        showo.add_argument("--order-id", type=int, required=True)
        showo.set_defaults(func=self._cmd_order_show)
        listo = porder_sub.add_parser("list", help="List all orders for a customer")
        listo.add_argument("--cust-id", type=int, required=True)
        listo.set_defaults(func=self._cmd_order_list)
        cano = porder_sub.add_parser("cancel", help="Cancel a placed order")
        cano.add_argument("--order-id", type=int, required=True)
        cano.set_defaults(func=self._cmd_order_cancel)
        
        # Payment commands
        p_pay = sub.add_parser("payment", help="Process payments")
        ppay_sub = p_pay.add_subparsers(dest="action", required=True)
        procp = ppay_sub.add_parser("process", help="Process a pending payment")
        procp.add_argument("--order-id", type=int, required=True)
        procp.add_argument("--method", required=True, choices=["Cash", "Card", "UPI"])
        procp.set_defaults(func=self._cmd_payment_process)

        # Report commands
        p_report = sub.add_parser("report", help="Generate reports")
        preport_sub = p_report.add_subparsers(dest="action", required=True)
        reps = preport_sub.add_parser("sales", help="Generate a sales summary report")
        reps.add_argument("--start-date", required=True, help="Format: YYYY-MM-DD")
        reps.add_argument("--end-date", required=True, help="Format: YYYY-MM-DD")
        reps.set_defaults(func=self._cmd_report_sales)

        return parser

def main():
    cli = RetailCLI()
    cli.run()

if __name__ == "__main__":
    main()