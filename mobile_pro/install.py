import frappe
from frappe import _

def after_install():
    """Setup Mobile Pro after installation"""
    try:
        setup_roles()
        create_default_settings()
        setup_number_series()
        create_sample_data()
        frappe.db.commit()
        print("Mobile Pro installation completed successfully!")
    except Exception as e:
        frappe.log_error(f"Installation error: {str(e)}")
        print(f"Installation error: {str(e)}")

def setup_roles():
    """Create default roles for Mobile Pro"""
    roles = [
        "Sales Manager", "Sales User", "Repair Manager", 
        "Technician", "Cashier", "POS Manager", 
        "Stock Manager", "Stock User"
    ]
    
    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            role = frappe.new_doc("Role")
            role.role_name = role_name
            role.save()

def create_default_settings():
    """Create default Mobile Pro settings"""
    
    # Create default Customer Group for walk-ins
    if not frappe.db.exists("Customer Group", "Walk-in"):
        customer_group = frappe.new_doc("Customer Group")
        customer_group.customer_group_name = "Walk-in"
        customer_group.parent_customer_group = "All Customer Groups"
        customer_group.save()
    
    # Create default Item Groups
    item_groups = ["Mobile Phones", "Tablets", "Accessories", "Repair Parts"]
    for group_name in item_groups:
        if not frappe.db.exists("Item Group", group_name):
            item_group = frappe.new_doc("Item Group")
            item_group.item_group_name = group_name
            item_group.parent_item_group = "All Item Groups"
            item_group.save()

def setup_number_series():
    """Setup number series for Mobile Pro documents"""
    series_list = [
        {
            "name": "MPO-.#####",
            "description": "Mobile Pro Order"
        },
        {
            "name": "REP-.#####", 
            "description": "Device Repair"
        },
        {
            "name": "POS-.######",
            "description": "Mobile Pro POS"
        },
        {
            "name": "COM-.#####",
            "description": "Commission Tracking"
        }
    ]
    
    for series in series_list:
        if not frappe.db.exists("Naming Series", series["name"]):
            naming_series = frappe.new_doc("Naming Series")
            naming_series.name = series["name"]
            naming_series.description = series["description"]
            naming_series.save()

def create_sample_data():
    """Create sample data for demonstration"""
    
    # Create sample customer
    if not frappe.db.exists("Customer", "Sample Customer"):
        customer = frappe.new_doc("Customer")
        customer.customer_name = "Sample Customer"
        customer.customer_type = "Individual"
        customer.customer_group = "Walk-in"
        customer.territory = "All Territories"
        customer.save()
    
    # Create sample items
    sample_items = [
        {
            "item_code": "IPHONE-14-128",
            "item_name": "iPhone 14 128GB",
            "item_group": "Mobile Phones",
            "standard_rate": 999.00
        },
        {
            "item_code": "SAMSUNG-S23-256", 
            "item_name": "Samsung Galaxy S23 256GB",
            "item_group": "Mobile Phones",
            "standard_rate": 899.00
        },
        {
            "item_code": "SCREEN-PROTECTOR",
            "item_name": "Screen Protector",
            "item_group": "Accessories", 
            "standard_rate": 19.99
        }
    ]
    
    for item_data in sample_items:
        if not frappe.db.exists("Item", item_data["item_code"]):
            item = frappe.new_doc("Item")
            item.item_code = item_data["item_code"]
            item.item_name = item_data["item_name"]
            item.item_group = item_data["item_group"]
            item.standard_rate = item_data["standard_rate"]
            item.stock_uom = "Nos"
            item.is_stock_item = 1
            item.save()

def before_uninstall():
    """Cleanup before uninstalling Mobile Pro"""
    print("Uninstalling Mobile Pro...")
    
def after_uninstall():
    """Cleanup after uninstalling Mobile Pro"""
    print("Mobile Pro uninstalled successfully!")