# Copyright (c) 2026, mahalakshmi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TicketsHd(Document):
    def validate(self):
        if self.project:
            project = frappe.get_doc("Project hd", self.project)

            if project.support_type == "Ad Hoc":
                frappe.throw(
                    "This project is under Ad Hoc support. Customers cannot raise tickets."
                )
                
# Copyright (c) 2026, mahalakshmi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date, now_datetime


# Change this to the actual enabled HelpDesk Agent User email.
DEFAULT_AGENT = "monishaa101@gmail.com"


class TicketsHd(Document):

    def before_insert(self):
        self.assign_default_agent()
        self.set_ticket_creator()
        self.set_default_status()
        self.set_sla_due_times()

    def validate(self):
        self.validate_ad_hoc_project()
        self.set_first_response_time()
        self.set_resolution_time()
        self.update_sla_status()

    def after_insert(self):
        self.send_assignment_email()

    def on_update(self):
        self.send_resolution_email()

    # ---------------------------------------------------------
    # Ticket setup
    # ---------------------------------------------------------

    def assign_default_agent(self):
        if not self.assigned_agent:
            self.assigned_agent = DEFAULT_AGENT

        if not self.assigned_on:
            self.assigned_on = now_datetime()

    def set_ticket_creator(self):
        if not self.ticket_raised_by:
            self.ticket_raised_by = frappe.session.user

        if not self.created_on:
            self.created_on = now_datetime()

    def set_default_status(self):
        if not self.status:
            self.status = "Open"

    def validate_ad_hoc_project(self):
        if not self.project:
            return

        support_type = frappe.db.get_value(
            "Project hd",
            self.project,
            "support_type"
        )

        if support_type == "Ad Hoc":
            frappe.throw(
                "This project is under Ad Hoc support. "
                "Customers cannot raise tickets."
            )

    # ---------------------------------------------------------
    # Email 1: New ticket assigned to agent
    # ---------------------------------------------------------

    def send_assignment_email(self):
        if not self.assigned_agent:
            frappe.log_error(
                title="Assignment Email Skipped",
                message=f"No assigned agent found for ticket {self.name}"
            )
            return

        frappe.sendmail(
            recipients=[self.assigned_agent],
            subject=f"New Ticket Assigned: {self.subject or self.name}",
            message=f"""
                <p>Dear Agent,</p>

                <p>A new helpdesk ticket has been assigned to you.</p>

                <table border="1" cellpadding="6"
                       cellspacing="0"
                       style="border-collapse: collapse;">
                    <tr>
                        <td><b>Ticket ID</b></td>
                        <td>{self.name}</td>
                    </tr>
                    <tr>
                        <td><b>Subject</b></td>
                        <td>{self.subject or ""}</td>
                    </tr>
                    <tr>
                        <td><b>Customer</b></td>
                        <td>{self.customer or ""}</td>
                    </tr>
                    <tr>
                        <td><b>Project</b></td>
                        <td>{self.project or ""}</td>
                    </tr>
                    <tr>
                        <td><b>Support Type</b></td>
                        <td>{self.support_type or ""}</td>
                    </tr>
                    <tr>
                        <td><b>Priority</b></td>
                        <td>{self.priority or ""}</td>
                    </tr>
                    <tr>
                        <td><b>Status</b></td>
                        <td>{self.status or "Open"}</td>
                    </tr>
                </table>

                <p>Please log in and start working on this ticket.</p>

                <p>
                    Regards,<br>
                    Maze Works Solution Helpdesk
                </p>
            """
        )

    # ---------------------------------------------------------
    # Email 2: Resolved ticket sent to customer
    # ---------------------------------------------------------

    def send_resolution_email(self):
        old_doc = self.get_doc_before_save()

        if not old_doc:
            return

        old_state = old_doc.workflow_state or old_doc.status
        new_state = self.workflow_state or self.status

        # Send only when the ticket changes into Resolved.
        if old_state == "Resolved" or new_state != "Resolved":
            return

        customer_email = self.get_customer_email()

        if not customer_email:
            frappe.log_error(
                title="Resolution Email Skipped",
                message=f"No customer email found for ticket {self.name}"
            )
            return

        frappe.sendmail(
            recipients=[customer_email],
            subject=f"Ticket Resolved: {self.subject or self.name}",
            message=f"""
                <p>Dear Customer,</p>

                <p>
                    Your helpdesk ticket has been successfully resolved.
                </p>

                <p><b>Ticket ID:</b> {self.name}</p>
                <p><b>Subject:</b> {self.subject or ""}</p>
                <p><b>Status:</b> Resolved</p>
                <p>
                    <b>Resolution:</b><br>
                    {self.resolution_detail or ""}
                </p>

                <p>
                    Regards,<br>
                    Maze Works Solution Helpdesk
                </p>
            """
        )

    def get_customer_email(self):
        if (
            self.ticket_raised_by
            and self.ticket_raised_by != "Guest"
        ):
            return self.ticket_raised_by

        if self.customer:
            return frappe.db.get_value(
                "Customer hd",
                self.customer,
                "portal_user"
            )

        return None

    # ---------------------------------------------------------
    # SLA calculation
    # ---------------------------------------------------------

    def set_sla_due_times(self):
        if not self.sla_policy:
            self.sla_policy = frappe.db.get_value(
                "SLA Policy",
                {
                    "enabled": 1,
                    "is_default": 1
                },
                "name"
            )

        if not self.sla_policy or not self.priority:
            return

        rule = frappe.db.get_value(
            "SLA Priority rules",
            {
                "parent": self.sla_policy,
                "priority": self.priority,
                "is_active": 1
            },
            [
                "first_response_time",
                "resolution_time"
            ],
            as_dict=True
        )

        if not rule:
            return

        created_time = now_datetime()

        self.first_response_due = add_to_date(
            created_time,
            hours=rule.first_response_time
        )

        self.resolution_due = add_to_date(
            created_time,
            hours=rule.resolution_time
        )

        self.sla_status = "Within SLA"

    def set_first_response_time(self):
        if self.first_responded_on:
            return

        current_state = self.workflow_state or self.status

        if current_state in (
            "Assigned",
            "In Progress",
            "Resolved",
            "Closed"
        ):
            self.first_responded_on = now_datetime()

    def set_resolution_time(self):
        current_state = self.workflow_state or self.status

        if current_state == "Resolved" and not self.resolved_on:
            self.resolved_on = now_datetime()

    def update_sla_status(self):
        current_time = now_datetime()
        current_state = self.workflow_state or self.status

        if current_state in ("Resolved", "Closed"):
            self.sla_status = "Completed"
            return

        if (
            self.resolution_due
            and current_time > self.resolution_due
        ):
            self.resolution_breached = 1
            self.sla_status = "Resolution Breached"
            return

        if (
            self.first_response_due
            and not self.first_responded_on
            and current_time > self.first_response_due
        ):
            self.response_breached = 1
            self.sla_status = "First Response Breached"
            return

        self.sla_status = "Within SLA"