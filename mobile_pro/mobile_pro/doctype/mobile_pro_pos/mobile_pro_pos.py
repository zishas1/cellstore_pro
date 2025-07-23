import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now

class MobileProPOS(Document):
    def before_save(self):
        self.generate_pos_id()
        self.calculate_totals()
        self.calculate_change()
    
    def generate_pos_id(self):
        """Generate unique POS ID if not exists"""
        if not self.pos_id:
            # Get the latest POS ID
            latest = frappe.db.sql("""
                SELECT pos_id 
                FROM `tabMobile Pro POS` 
                WHERE pos_id LIKE 'POS-%' 
                ORDER BY creation DESC 
                LIMIT 1
            """)
            
            if latest:
                last_num = int(latest[0][0].split('-')[1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.pos_id = f"POS-{new_num:06d}"
    
    def calculate_totals(self):
        """Calculate subtotal, tax, and total amounts"""
        subtotal = 0
        
        for item in self.items:
            # Calculate item amount
            item.amount = flt(item.quantity) * flt(item.rate)
            
            # Apply discount
            if item.discount_percent:
                item.discount_amount = (item.amount * flt(item.discount_percent)) / 100
                item.amount -= item.discount_amount
            
            subtotal += item.amount
        
        self.subtotal = subtotal
        
        # Calculate total
        total = subtotal + flt(self.tax_amount) - flt(self.discount_amount)
        self.total_amount = total
    
    def calculate_change(self):
        """Calculate change amount"""
        if self.amount_paid and self.total_amount:
            self.change_amount = flt(self.amount_paid) - flt(self.total_amount)
        else:
            self.change_amount = 0
    
    def on_submit(self):
        """Actions to perform on POS transaction submission"""
        self.update_inventory()
        self.create_order_record()
        self.update_serial_numbers()
    
    def update_inventory(self):
        """Update inventory for sold items"""
        for item in self.items:
            # Update stock levels (this would integrate with ERPNext stock system)
            try:
                # Create stock entry or update bin
                frappe.db.sql("""
                    UPDATE `tabBin` 
                    SET actual_qty = actual_qty - %s 
                    WHERE item_code = %s
                """, (item.quantity, item.item_code))
            except Exception as e:
                frappe.log_error(f"Failed to update inventory for {item.item_code}: {str(e)}")
    
    def create_order_record(self):
        """Create corresponding Mobile Pro Order record"""
        if not self.customer:
            # Create walk-in customer
            customer = self.create_walk_in_customer()
        else:
            customer = self.customer
        
        # Create order
        order = frappe.new_doc("Mobile Pro Order")
        order.customer = customer
        order.sales_representative = self.cashier
        order.order_date = self.transaction_date
        order.status = "Delivered"  # POS sales are immediately delivered
        order.payment_status = "Paid"
        
        # Add items
        for pos_item in self.items:
            order.append("items", {
                "item_code": pos_item.item_code,
                "item_name": pos_item.item_name,
                "quantity": pos_item.quantity,
                "rate": pos_item.rate,
                "amount": pos_item.amount,
                "serial_numbers": pos_item.serial_number
            })
        
        order.save()
        order.submit()
        
        # Link the order to this POS transaction
        self.db_set("order_reference", order.name)
    
    def create_walk_in_customer(self):
        """Create a walk-in customer record"""
        customer_name = f"Walk-in Customer {self.pos_id}"
        
        customer = frappe.new_doc("Customer")
        customer.customer_name = customer_name
        customer.customer_type = "Individual"
        customer.customer_group = "Walk-in"
        customer.territory = "All Territories"
        customer.save()
        
        return customer.name
    
    def update_serial_numbers(self):
        """Update serial number status for sold items"""
        for item in self.items:
            if item.serial_number:
                # Update serial number tracking
                serial_doc = frappe.db.exists("Serial Number Tracking", {
                    "serial_number": item.serial_number
                })
                
                if serial_doc:
                    frappe.db.set_value("Serial Number Tracking", serial_doc, {
                        "status": "Sold",
                        "customer": self.customer,
                        "sale_date": self.transaction_date
                    })

@frappe.whitelist()
def get_item_details_for_pos(item_code):
    """Get item details for POS including current stock"""
    if not item_code:
        return {}
    
    item = frappe.get_doc("Item", item_code)
    
    # Get current stock
    stock_qty = frappe.db.sql("""
        SELECT actual_qty 
        FROM `tabBin` 
        WHERE item_code = %s
    """, item_code)
    
    current_stock = stock_qty[0][0] if stock_qty else 0
    
    # Get available serial numbers for serialized items
    serial_numbers = []
    if item.has_serial_no:
        serials = frappe.get_all("Serial Number Tracking",
            filters={
                "item_code": item_code,
                "status": "In Stock"
            },
            fields=["serial_number"]
        )
        serial_numbers = [s.serial_number for s in serials]
    
    return {
        "item_name": item.item_name,
        "rate": item.standard_rate or 0,
        "description": item.description,
        "current_stock": current_stock,
        "has_serial_no": item.has_serial_no,
        "available_serials": serial_numbers,
        "item_group": item.item_group,
        "brand": getattr(item, 'brand', ''),
        "barcode": getattr(item, 'barcode', '')
    }

@frappe.whitelist()
def process_pos_payment(pos_id, payment_method, amount_paid):
    """Process payment for POS transaction"""
    pos_doc = frappe.get_doc("Mobile Pro POS", pos_id)
    
    if pos_doc.docstatus == 1:
        return {"error": "Transaction already processed"}
    
    pos_doc.payment_method = payment_method
    pos_doc.amount_paid = amount_paid
    pos_doc.save()
    pos_doc.submit()
    
    return {
        "success": True,
        "pos_id": pos_id,
        "change_amount": pos_doc.change_amount,
        "total_amount": pos_doc.total_amount
    }

@frappe.whitelist()
def get_pos_summary(cashier, from_date, to_date):
    """Get POS summary for a cashier"""
    transactions = frappe.get_all("Mobile Pro POS",
        filters={
            "cashier": cashier,
            "transaction_date": ["between", [from_date, to_date]],
            "docstatus": 1
        },
        fields=["pos_id", "transaction_date", "total_amount", "payment_method"]
    )
    
    # Calculate summary
    total_sales = sum(t.total_amount for t in transactions)
    
    # Group by payment method
    payment_summary = {}
    for t in transactions:
        method = t.payment_method or "Unknown"
        if method not in payment_summary:
            payment_summary[method] = {"count": 0, "amount": 0}
        payment_summary[method]["count"] += 1
        payment_summary[method]["amount"] += t.total_amount
    
    return {
        "cashier": cashier,
        "period": f"{from_date} to {to_date}",
        "total_transactions": len(transactions),
        "total_sales": total_sales,
        "payment_methods": payment_summary,
        "transactions": transactions
    }

@frappe.whitelist()
def get_daily_pos_report(date):
    """Get daily POS report for all cashiers"""
    transactions = frappe.get_all("Mobile Pro POS",
        filters={
            "transaction_date": date,
            "docstatus": 1
        },
        fields=["cashier", "pos_id", "total_amount", "payment_method", "transaction_time"]
    )
    
    # Group by cashier
    cashier_summary = {}
    for t in transactions:
        cashier = t.cashier
        if cashier not in cashier_summary:
            cashier_summary[cashier] = {
                "transactions": 0,
                "total_amount": 0,
                "payment_methods": {}
            }
        
        cashier_summary[cashier]["transactions"] += 1
        cashier_summary[cashier]["total_amount"] += t.total_amount
        
        method = t.payment_method or "Unknown"
        if method not in cashier_summary[cashier]["payment_methods"]:
            cashier_summary[cashier]["payment_methods"][method] = 0
        cashier_summary[cashier]["payment_methods"][method] += t.total_amount
    
    return {
        "date": date,
        "total_transactions": len(transactions),
        "total_sales": sum(t.total_amount for t in transactions),
        "cashier_summary": cashier_summary,
        "transactions": transactions
    }