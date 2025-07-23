import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now, add_days, get_datetime

class DeviceRepair(Document):
    def before_save(self):
        self.generate_repair_id()
        self.calculate_costs()
        self.validate_dates()
    
    def generate_repair_id(self):
        """Generate unique repair ID if not exists"""
        if not self.repair_id:
            # Get the latest repair ID
            latest = frappe.db.sql("""
                SELECT repair_id 
                FROM `tabDevice Repair` 
                WHERE repair_id LIKE 'REP-%' 
                ORDER BY creation DESC 
                LIMIT 1
            """)
            
            if latest:
                last_num = int(latest[0][0].split('-')[1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.repair_id = f"REP-{new_num:05d}"
    
    def calculate_costs(self):
        """Calculate total actual cost from parts and labor"""
        if self.parts_cost or self.labor_cost:
            self.actual_cost = flt(self.parts_cost) + flt(self.labor_cost)
    
    def validate_dates(self):
        """Validate date relationships"""
        if self.estimated_completion and self.date_received:
            if get_datetime(self.estimated_completion) < get_datetime(self.date_received):
                frappe.throw(_("Estimated completion date cannot be before received date"))
        
        if self.actual_completion and self.date_received:
            if get_datetime(self.actual_completion) < get_datetime(self.date_received):
                frappe.throw(_("Actual completion date cannot be before received date"))
    
    def on_update(self):
        """Actions to perform on document update"""
        self.send_status_notification()
    
    def send_status_notification(self):
        """Send notification to customer on status changes"""
        if self.has_value_changed("repair_status"):
            # Create notification/communication for customer
            if self.repair_status in ["Completed", "Ready for Pickup"]:
                self.create_completion_notification()
    
    def create_completion_notification(self):
        """Create notification when repair is completed"""
        try:
            # Create a communication record
            comm = frappe.new_doc("Communication")
            comm.communication_type = "Notification"
            comm.subject = f"Device Repair Update - {self.repair_id}"
            comm.content = f"""
                Dear Customer,
                
                Your device repair with ID {self.repair_id} has been {self.repair_status.lower()}.
                
                Device: {self.device_brand} {self.device_model}
                Status: {self.repair_status}
                {"Actual Cost: " + str(self.actual_cost) if self.actual_cost else ""}
                {"Warranty Period: " + str(self.warranty_period) + " days" if self.warranty_period else ""}
                
                Please contact us to arrange pickup/delivery.
                
                Thank you for choosing Mobile Pro!
            """
            comm.reference_doctype = "Device Repair"
            comm.reference_name = self.name
            comm.save()
        except Exception as e:
            # Log error but don't stop the process
            frappe.log_error(f"Failed to create notification: {str(e)}")
    
    def get_repair_summary(self):
        """Get summary information for this repair"""
        return {
            "repair_id": self.repair_id,
            "customer": self.customer,
            "device": f"{self.device_brand} {self.device_model}",
            "status": self.repair_status,
            "priority": self.priority,
            "days_in_repair": (get_datetime(now()) - get_datetime(self.date_received)).days,
            "estimated_cost": self.estimated_cost,
            "actual_cost": self.actual_cost,
            "warranty_expires": add_days(self.actual_completion, self.warranty_period) if self.actual_completion else None
        }

@frappe.whitelist()
def get_repair_statistics():
    """Get repair statistics for dashboard"""
    stats = {}
    
    # Count by status
    status_counts = frappe.db.sql("""
        SELECT repair_status, COUNT(*) as count
        FROM `tabDevice Repair`
        GROUP BY repair_status
    """, as_dict=True)
    
    stats['status_breakdown'] = {item['repair_status']: item['count'] for item in status_counts}
    
    # Priority breakdown
    priority_counts = frappe.db.sql("""
        SELECT priority, COUNT(*) as count
        FROM `tabDevice Repair`
        GROUP BY priority
    """, as_dict=True)
    
    stats['priority_breakdown'] = {item['priority']: item['count'] for item in priority_counts}
    
    # Average repair time for completed repairs
    avg_time = frappe.db.sql("""
        SELECT AVG(DATEDIFF(actual_completion, date_received)) as avg_days
        FROM `tabDevice Repair`
        WHERE actual_completion IS NOT NULL
    """)
    
    stats['average_repair_days'] = round(avg_time[0][0], 1) if avg_time[0][0] else 0
    
    # Revenue statistics
    revenue_stats = frappe.db.sql("""
        SELECT 
            SUM(actual_cost) as total_revenue,
            COUNT(*) as completed_repairs
        FROM `tabDevice Repair`
        WHERE repair_status = 'Delivered' AND actual_cost > 0
    """, as_dict=True)
    
    stats['revenue_stats'] = revenue_stats[0] if revenue_stats else {}
    
    return stats

@frappe.whitelist()
def get_technician_workload(technician=None):
    """Get workload for a specific technician or all technicians"""
    filters = {"repair_status": ["not in", ["Delivered", "Cancelled"]]}
    
    if technician:
        filters["technician_assigned"] = technician
    
    repairs = frappe.get_all("Device Repair",
        filters=filters,
        fields=["technician_assigned", "repair_status", "priority", "date_received"]
    )
    
    workload = {}
    for repair in repairs:
        tech = repair.technician_assigned or "Unassigned"
        if tech not in workload:
            workload[tech] = {
                "total": 0,
                "urgent": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "overdue": 0
            }
        
        workload[tech]["total"] += 1
        workload[tech][repair.priority.lower()] += 1
        
        # Check if overdue (more than 7 days)
        days_elapsed = (get_datetime(now()) - get_datetime(repair.date_received)).days
        if days_elapsed > 7:
            workload[tech]["overdue"] += 1
    
    return workload

@frappe.whitelist()
def assign_repair_to_technician(repair_id, technician):
    """Assign a repair to a technician"""
    repair = frappe.get_doc("Device Repair", repair_id)
    repair.technician_assigned = technician
    if repair.repair_status == "Received":
        repair.repair_status = "Diagnosed"
    repair.save()
    
    return {"success": True, "message": f"Repair {repair_id} assigned to {technician}"}

@frappe.whitelist()
def update_repair_status(repair_id, new_status, completion_date=None):
    """Update repair status and handle completion logic"""
    repair = frappe.get_doc("Device Repair", repair_id)
    repair.repair_status = new_status
    
    if new_status == "Completed" and completion_date:
        repair.actual_completion = completion_date
    
    repair.save()
    
    return {"success": True, "message": f"Repair status updated to {new_status}"}