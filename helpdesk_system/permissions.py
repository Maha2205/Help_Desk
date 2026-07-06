import frappe

def get_ticket_permission_query(user):
    if user == "Administrator":
        return ""

    roles = frappe.get_roles(user)

    if "Helpdesk Customer" in roles:
        customer = frappe.db.get_value(
            "Customer hd",
            {"user": user},
            "name"
        )

        if customer:
            return f"`tabTickets Hd`.customer = '{customer}'"

    return ""