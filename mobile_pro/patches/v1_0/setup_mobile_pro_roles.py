import frappe

def execute():
    """Setup Mobile Pro specific roles"""
    
    roles = [
        {
            "role_name": "Sales Manager",
            "description": "Can manage sales operations and commission tracking"
        },
        {
            "role_name": "Sales User", 
            "description": "Can create orders and manage customers"
        },
        {
            "role_name": "Repair Manager",
            "description": "Can manage device repairs and assign technicians"
        },
        {
            "role_name": "Technician",
            "description": "Can update repair status and add technical notes"
        },
        {
            "role_name": "Cashier",
            "description": "Can process POS transactions"
        },
        {
            "role_name": "POS Manager",
            "description": "Can manage POS operations and view reports"
        },
        {
            "role_name": "Stock Manager",
            "description": "Can manage inventory and serial number tracking"
        },
        {
            "role_name": "Stock User",
            "description": "Can view and update stock information"
        }
    ]
    
    for role_data in roles:
        if not frappe.db.exists("Role", role_data["role_name"]):
            role = frappe.new_doc("Role")
            role.role_name = role_data["role_name"]
            role.description = role_data["description"]
            role.save()
            
    frappe.db.commit()
    print("Mobile Pro roles created successfully")