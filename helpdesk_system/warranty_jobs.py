import frappe
from frappe.utils import add_days, add_months, getdate, today

def send_warranty_amc_notifications():
    current_date = getdate(today())

    projects = frappe.get_all(
        "Project hd",
        fields=[
            "name",
            "start_date",
            "end_date",
            "support_type",
            "customer_email"
        ]
    )

    for project in projects:
        if not project.customer_email:
            continue

        doc = frappe.get_doc("Project hd", project.name)

        support_type = (project.support_type or "").strip().lower()

        # 1. Free warranty reminder:
        # Send 2 days before completing 2 months
        if project.start_date:
            free_warranty_end = getdate(
                add_months(project.start_date, 2)
            )

            if current_date == getdate(
                add_days(free_warranty_end, -2)
            ):
                send_notification(
                    "Free Warranty Expiry Reminder",
                    doc
                )

        if not project.end_date:
            continue

        end_date = getdate(project.end_date)

        # 2. Warranty reminder — 5 days before
        if (
            support_type == "warranty"
            and current_date == getdate(add_days(end_date, -5))
        ):
            send_notification(
                "Warranty Expiry Reminder",
                doc
            )

        # 3. Warranty expired — on expiry date
        if (
            support_type == "warranty"
            and current_date == end_date
        ):
            send_notification(
                "Warranty Expired Notification",
                doc
            )

        # 4. AMC reminder — 5 days before
        if (
            support_type == "amc"
            and current_date == getdate(add_days(end_date, -5))
        ):
            send_notification(
                "AMC Renewal Reminder",
                doc
            )

        # 5. AMC expired — on expiry date
        if (
            support_type == "amc"
            and current_date == end_date
        ):
            send_notification(
                "AMC Expired Notification",
                doc
            )


def send_notification(notification_name, doc):
    if not frappe.db.exists("Notification", notification_name):
        frappe.log_error(
            title="Notification Not Found",
            message=f"Notification not found: {notification_name}"
        )
        return

    notification = frappe.get_doc(
        "Notification",
        notification_name
    )

    if notification.enabled:
        notification.send(doc)   