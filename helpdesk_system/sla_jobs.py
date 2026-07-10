import frappe
from frappe.utils import now_datetime

def check_sla_breaches():
    now = now_datetime()

    tickets = frappe.get_all(
        "Tickets Hd",
        filters={
            "status": ["not in", ["Resolved", "Closed"]]
        },
        fields=[
            "name",
            "first_response_due",
            "resolution_due",
            "response_breached",
            "resolution_breached"
        ]
    )

    for ticket in tickets:
        if ticket.first_response_due and ticket.first_response_due < now:
            frappe.db.set_value("Tickets Hd", ticket.name, "response_breached", 1)

        if ticket.resolution_due and ticket.resolution_due < now:
            frappe.db.set_value("Tickets Hd", ticket.name, "resolution_breached", 1)

    frappe.db.commit()