import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now, add_months

class MobileProOrder(Document):
    def before_save(self):
        self.calculate_totals()
        self.generate_order_number()
    
    def calculate_totals(self):
        """Calculate totals for the order"""
        total_amount = 0
        total_cost = 0
        total_commission = 0
        
        for item in self.items:
            # Calculate item amount
            item.amount = flt(item.quantity) * flt(item.rate)
            total_amount += item.amount
            
            # Calculate profit
            if item.cost_price:
                item.profit = item.amount - (flt(item.quantity) * flt(item.cost_price))
                total_cost += flt(item.quantity) * flt(item.cost_price)
            
            # Calculate commission
            if item.commission_rate:
                commission = (item.amount * flt(item.commission_rate)) / 100
                item.commission_amount = commission
                total_commission += commission
        
        self.total_amount = total_amount
        self.profit_margin = total_amount - total_cost
        self.commission_amount = total_commission
    
    def generate_order_number(self):
        """Generate unique order number if not exists"""
        if not self.order_number:
            # Get the latest order number
            latest = frappe.db.sql("""
                SELECT order_number 
                FROM `tabMobile Pro Order` 
                WHERE order_number LIKE 'MPO-%' 
                ORDER BY creation DESC 
                LIMIT 1
            """)
            
            if latest:
                last_num = int(latest[0][0].split('-')[1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.order_number = f"MPO-{new_num:05d}"
    
    def on_submit(self):
        """Actions to perform on order submission"""
        self.create_commission_record()
        self.update_serial_numbers()
    
    def create_commission_record(self):
        """Create commission tracking record for sales representative"""
        if self.sales_representative and self.commission_amount > 0:
            # Check if commission record exists for this period
            period_start = frappe.utils.get_first_day(self.order_date)
            period_end = frappe.utils.get_last_day(self.order_date)
            
            commission_doc = frappe.db.exists("Commission Tracking", {
                "sales_rep": self.sales_representative,
                "period_start": period_start,
                "period_end": period_end
            })
            
            if commission_doc:
                # Update existing commission record
                comm = frappe.get_doc("Commission Tracking", commission_doc)
                comm.append("commission_details", {
                    "order_reference": self.name,
                    "order_date": self.order_date,
                    "order_amount": self.total_amount,
                    "commission_amount": self.commission_amount
                })
                comm.save()
            else:
                # Create new commission record
                comm = frappe.new_doc("Commission Tracking")
                comm.sales_rep = self.sales_representative
                comm.period_start = period_start
                comm.period_end = period_end
                comm.commission_rate = 5  # Default 5%
                comm.append("commission_details", {
                    "order_reference": self.name,
                    "order_date": self.order_date,
                    "order_amount": self.total_amount,
                    "commission_amount": self.commission_amount
                })
                comm.save()
    
    def update_serial_numbers(self):
        """Update serial number tracking for items"""
        for item in self.items:
            if item.serial_numbers:
                serial_list = [s.strip() for s in item.serial_numbers.split(',')]
                for serial in serial_list:
                    if serial:
                        # Create or update serial number tracking
                        serial_doc = frappe.new_doc("Serial Number Tracking")
                        serial_doc.serial_number = serial
                        serial_doc.item_code = item.item_code
                        serial_doc.customer = self.customer
                        serial_doc.order_reference = self.name
                        serial_doc.sale_date = self.order_date
                        serial_doc.status = "Sold"
                        try:
                            serial_doc.save()
                        except:
                            frappe.throw(_("Serial Number {0} already exists").format(serial))

@frappe.whitelist()
def get_item_details(item_code):
    """Get item details for the selected item"""
    if not item_code:
        return {}
    
    item = frappe.get_doc("Item", item_code)
    return {
        "item_name": item.item_name,
        "rate": item.standard_rate or 0,
        "description": item.description
    }

@frappe.whitelist()
def get_commission_summary(sales_rep, from_date, to_date):
    """Get commission summary for a sales representative"""
    orders = frappe.get_all("Mobile Pro Order", 
        filters={
            "sales_representative": sales_rep,
            "order_date": ["between", [from_date, to_date]],
            "docstatus": 1
        },
        fields=["name", "order_date", "total_amount", "commission_amount"]
    )
    
    total_sales = sum(order.total_amount for order in orders)
    total_commission = sum(order.commission_amount for order in orders)
    
    return {
        "orders": orders,
        "total_sales": total_sales,
        "total_commission": total_commission,
        "order_count": len(orders)
    }