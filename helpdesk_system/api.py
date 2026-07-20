import frappe

@frappe.whitelist()
def create_adhoc_customer_project(data):

    data = frappe.parse_json(data)

    customer_name = data.get("customer_name")
    project_name = data.get("project_name")
    email_id = data.get("email_id")
    mobile_no = data.get("mobile_no")

    # Check if customer already exists
    existing_customer = frappe.db.exists(
        "Customer hd",
        {"customer_name": customer_name}
    )

    if existing_customer:
        customer = existing_customer
    else:
        customer = frappe.get_doc({
            "doctype": "Customer hd",
            "customer_name": customer_name,
            "email_id": email_id,
            "mobile_no": mobile_no
        }).insert(ignore_permissions=True).name

    project = frappe.get_doc({
        "doctype": "Project hd",
        "customer": customer,
        "project_name": project_name,
        "support_type": "Ad Hoc"
    }).insert(ignore_permissions=True).name

    return {
        "customer": customer,
        "project": project
    }