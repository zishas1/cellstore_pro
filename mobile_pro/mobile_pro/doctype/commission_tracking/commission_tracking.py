import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now, get_first_day, get_last_day

class CommissionTracking(Document):
    def before_save(self):
        self.calculate_commission_totals()
        self.set_calculation_date()
    
    def calculate_commission_totals(self):
        """Calculate total sales and commission amounts"""
        total_sales = 0
        base_commission = 0
        
        for detail in self.commission_details:
            total_sales += flt(detail.order_amount)
            base_commission += flt(detail.commission_amount)
        
        self.total_sales = total_sales
        self.base_commission = base_commission
        self.total_commission = base_commission + flt(self.bonus_commission)
    
    def set_calculation_date(self):
        """Set calculation date when status changes to Calculated"""
        if self.status == "Calculated" and not self.calculation_date:
            self.calculation_date = now()
    
    def validate(self):
        """Validate commission tracking data"""
        if self.period_start > self.period_end:
            frappe.throw(_("Period start date cannot be after period end date"))
        
        # Check for overlapping periods for the same sales rep
        existing = frappe.db.sql("""
            SELECT name FROM `tabCommission Tracking`
            WHERE sales_rep = %s 
            AND name != %s
            AND (
                (period_start <= %s AND period_end >= %s) OR
                (period_start <= %s AND period_end >= %s) OR
                (period_start >= %s AND period_end <= %s)
            )
        """, (self.sales_rep, self.name or "", 
              self.period_start, self.period_start,
              self.period_end, self.period_end,
              self.period_start, self.period_end))
        
        if existing:
            frappe.throw(_("Overlapping commission period exists for this sales representative"))
    
    def on_submit(self):
        """Actions to perform on submission"""
        self.status = "Approved"
    
    def get_commission_summary(self):
        """Get detailed commission summary"""
        return {
            "sales_rep": self.sales_rep,
            "period": f"{self.period_start} to {self.period_end}",
            "total_orders": len(self.commission_details),
            "total_sales": self.total_sales,
            "commission_rate": self.commission_rate,
            "base_commission": self.base_commission,
            "bonus_commission": self.bonus_commission,
            "total_commission": self.total_commission,
            "status": self.status
        }

@frappe.whitelist()
def create_monthly_commission(sales_rep, month, year):
    """Create monthly commission tracking for a sales representative"""
    from datetime import datetime
    
    # Calculate period dates
    period_start = datetime(int(year), int(month), 1).date()
    period_end = get_last_day(period_start)
    
    # Check if commission already exists
    existing = frappe.db.exists("Commission Tracking", {
        "sales_rep": sales_rep,
        "period_start": period_start,
        "period_end": period_end
    })
    
    if existing:
        return {"error": "Commission tracking already exists for this period"}
    
    # Get orders for the period
    orders = frappe.get_all("Mobile Pro Order",
        filters={
            "sales_representative": sales_rep,
            "order_date": ["between", [period_start, period_end]],
            "docstatus": 1
        },
        fields=["name", "order_date", "total_amount", "commission_amount"]
    )
    
    if not orders:
        return {"error": "No orders found for this period"}
    
    # Create commission tracking document
    commission_doc = frappe.new_doc("Commission Tracking")
    commission_doc.sales_rep = sales_rep
    commission_doc.period_start = period_start
    commission_doc.period_end = period_end
    commission_doc.commission_rate = 5  # Default 5%
    commission_doc.status = "Draft"
    
    # Add commission details
    for order in orders:
        commission_doc.append("commission_details", {
            "order_reference": order.name,
            "order_date": order.order_date,
            "order_amount": order.total_amount,
            "commission_amount": order.commission_amount
        })
    
    commission_doc.save()
    
    return {
        "success": True,
        "commission_doc": commission_doc.name,
        "total_orders": len(orders),
        "total_commission": commission_doc.total_commission
    }

@frappe.whitelist()
def approve_commission(commission_name, approver):
    """Approve commission tracking document"""
    commission_doc = frappe.get_doc("Commission Tracking", commission_name)
    
    if commission_doc.status not in ["Calculated"]:
        return {"error": "Commission can only be approved when in Calculated status"}
    
    commission_doc.status = "Approved"
    commission_doc.approved_by = approver
    commission_doc.save()
    
    return {"success": True, "message": "Commission approved successfully"}

@frappe.whitelist()
def mark_commission_paid(commission_name, payment_date, payment_reference):
    """Mark commission as paid"""
    commission_doc = frappe.get_doc("Commission Tracking", commission_name)
    
    if commission_doc.status != "Approved":
        return {"error": "Commission must be approved before marking as paid"}
    
    commission_doc.status = "Paid"
    commission_doc.payment_date = payment_date
    commission_doc.payment_reference = payment_reference
    commission_doc.save()
    
    return {"success": True, "message": "Commission marked as paid"}

@frappe.whitelist()
def get_sales_rep_performance(sales_rep, from_date, to_date):
    """Get comprehensive performance data for a sales representative"""
    
    # Get commission records
    commissions = frappe.get_all("Commission Tracking",
        filters={
            "sales_rep": sales_rep,
            "period_start": [">=", from_date],
            "period_end": ["<=", to_date]
        },
        fields=["period_start", "period_end", "total_sales", "total_commission", "status"]
    )
    
    # Get individual orders
    orders = frappe.get_all("Mobile Pro Order",
        filters={
            "sales_representative": sales_rep,
            "order_date": ["between", [from_date, to_date]],
            "docstatus": 1
        },
        fields=["order_date", "total_amount", "commission_amount", "customer"]
    )
    
    # Calculate summary statistics
    total_sales = sum(order.total_amount for order in orders)
    total_commission = sum(comm.total_commission for comm in commissions)
    avg_order_value = total_sales / len(orders) if orders else 0
    
    return {
        "sales_rep": sales_rep,
        "period": f"{from_date} to {to_date}",
        "summary": {
            "total_orders": len(orders),
            "total_sales": total_sales,
            "total_commission": total_commission,
            "average_order_value": avg_order_value
        },
        "commissions": commissions,
        "recent_orders": orders[-10:]  # Last 10 orders
    }