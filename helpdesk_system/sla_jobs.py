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
            "subject",
            "status",
            "priority",
            "ticket_raised_by",
            "customer",
            "first_response_due",
            "resolution_due",
            "first_responded_on",
            "response_breached",
            "resolution_breached"
        ]
    )

    for ticket in tickets:

        # Resolution breach has higher priority.
        if (
            ticket.resolution_due
            and current_time > ticket.resolution_due
            and not ticket.resolution_breached
        ):
            frappe.db.set_value(
                "Tickets Hd",
                ticket.name,
                {
                    "resolution_breached": 1,
                    "sla_status": "Resolution Breached"
                }
            )

            send_resolution_breach_email(ticket)
            continue

        # First response breach.
        if (
            ticket.first_response_due
            and not ticket.first_responded_on
            and current_time > ticket.first_response_due
            and not ticket.response_breached
        ):
            frappe.db.set_value(
                "Tickets Hd",
                ticket.name,
                {
                    "response_breached": 1,
                    "sla_status": "First Response Breached"
                }
            )

            send_first_response_breach_email(ticket)

    frappe.db.commit()


def get_customer_email(ticket):
    if (
        ticket.ticket_raised_by
        and ticket.ticket_raised_by != "Guest"
    ):
        return ticket.ticket_raised_by

    if ticket.customer:
        return frappe.db.get_value(
            "Customer hd",
            ticket.customer,
            "portal_user"
        )

    return None


def send_first_response_breach_email(ticket):
    customer_email = get_customer_email(ticket)

    if not customer_email:
        frappe.log_error(
            title="First Response Breach Email Skipped",
            message=f"No customer email found for ticket {ticket.name}"
        )
        return

    frappe.sendmail(
        recipients=[customer_email],
        subject=(
            f"SLA Alert: First Response Breached - "
            f"{ticket.subject or ticket.name}"
        ),
        message=f"""
            <h3>First Response SLA Breached</h3>

            <p>Dear Customer,</p>

            <p>
                The first response time for your support ticket
                has exceeded the configured SLA.
            </p>

            <p><b>Ticket ID:</b> {ticket.name}</p>
            <p><b>Subject:</b> {ticket.subject or ""}</p>
            <p><b>Status:</b> {ticket.status or ""}</p>
            <p><b>Priority:</b> {ticket.priority or ""}</p>
            <p>
                <b>First Response Due:</b>
                {ticket.first_response_due or ""}
            </p>

            <p>
                Our support team has been notified and will respond
                as soon as possible.
            </p>

            <p>
                Regards,<br>
                Maze Works Solution Helpdesk
            </p>
        """
    )


def send_resolution_breach_email(ticket):
    customer_email = get_customer_email(ticket)

    if not customer_email:
        frappe.log_error(
            title="Resolution Breach Email Skipped",
            message=f"No customer email found for ticket {ticket.name}"
        )
        return

    frappe.sendmail(
        recipients=[customer_email],
        subject=(
            f"SLA Alert: Resolution Breached - "
            f"{ticket.subject or ticket.name}"
        ),
        message=f"""
            <h3>Resolution SLA Breached</h3>

            <p>Dear Customer,</p>

            <p>
                The resolution time for your support ticket
                has exceeded the configured SLA.
            </p>

            <p><b>Ticket ID:</b> {ticket.name}</p>
            <p><b>Subject:</b> {ticket.subject or ""}</p>
            <p><b>Status:</b> {ticket.status or ""}</p>
            <p><b>Priority:</b> {ticket.priority or ""}</p>
            <p>
                <b>Resolution Due:</b>
                {ticket.resolution_due or ""}
            </p>

            <p>
                Our support team is actively working to resolve
                your issue as quickly as possible.
            </p>

            <p>
                Regards,<br>
                Maze Works Solution Helpdesk
            </p>
        """
    )