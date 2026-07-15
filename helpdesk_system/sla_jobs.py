import frappe
from frappe.utils import now_datetime


def check_sla_breaches():
    current_time = now_datetime()

    tickets = frappe.get_all(
        "Tickets Hd",
        filters={
            "status": ["not in", ["Resolved", "Closed"]]
        },
        fields=[
            "name",
            "first_response_due",
            "resolution_due",
            "first_responded_on",
            "response_breached",
            "resolution_breached"
        ]
    )

    for ticket in tickets:
        doc = frappe.get_doc("Tickets Hd", ticket.name)
        changed = False

        # Resolution breach
        if (
            doc.resolution_due
            and current_time > doc.resolution_due
            and not doc.resolution_breached
        ):
            doc.resolution_breached = 1
            doc.sla_status = "Resolution Breached"
            changed = True

        # First response breach
        elif (
            doc.first_response_due
            and current_time > doc.first_response_due
            and not doc.first_responded_on
            and not doc.response_breached
        ):
            doc.response_breached = 1
            doc.sla_status = "First Response Breached"
            changed = True

        if changed:
            doc.save(ignore_permissions=True)

    frappe.db.commit()