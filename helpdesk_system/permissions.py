import frappe

def get_ticket_permission_query(user):

    if user == "Administrator":
        return ""

    roles = frappe.get_roles(user)

    if "Helpdesk Customer" in roles:

        customer = frappe.db.get_value(
            "Customer hd",
            {
                "portal_user": user
            },
            "name"
        )

        if customer:
            return f"`tabTickets Hd`.customer = {frappe.db.escape(customer)}"

        # If no linked customer, show no tickets
        return "1=0"

    return ""