import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime, today


DEFAULT_AGENT = "monishaa101@gmail.com"


class TicketsHd(Document):

    def before_insert(self):
        if not self.assigned_agent:
            self.assigned_agent = DEFAULT_AGENT

        if not self.assigned_on:
            self.assigned_on = now_datetime()

        if not self.status:
            self.status = "Open"

        if not self.workflow_state:
            self.workflow_state = "Open"

    def validate(self):
        self.validate_project_support()
        self.sync_status_with_workflow()

    def validate_project_support(self):
        if not self.project or not self.customer:
            return

        project_details = frappe.db.get_value(
            "Project hd",
            self.project,
            [
                "support_type",
                "end_date"
            ],
            as_dict=True
        )

        if not project_details:
            return

        customer_user = frappe.db.get_value(
            "Customer hd",
            self.customer,
            "portal_user"
        )

        # Apply this restriction only when the customer is logged in
        if frappe.session.user != customer_user:
            return

        # Ad Hoc customers cannot raise tickets
        if project_details.support_type == "Ad Hoc":
            frappe.throw(
                "This project is under Ad Hoc support. "
                " Dear Customer you can't raise tickets please contact the admin."
            )

        # Check the common End Date for AMC and Warranty
        if (
            project_details.support_type in ["AMC", "Warranty"]
            and project_details.end_date
            and getdate(project_details.end_date) <= getdate(today())
        ):
            frappe.throw(
                f"The {project_details.support_type} support period "
                f"for this project expired on "
                f"{project_details.end_date}. "
                "You cannot raise a new ticket. "
                "Please contact the administrator."
            )

    def sync_status_with_workflow(self):

        if self.workflow_state == "Assigned":
            self.status = "Assigned"

            if not self.first_responded_on:
                self.first_responded_on = now_datetime()

        elif self.workflow_state == "In progress":
            self.status = "In progress"

            if not self.first_responded_on:
                self.first_responded_on = now_datetime()

        elif self.workflow_state == "Resolved":
            self.status = "Resolved"

            if not self.resolved_on:
                self.resolved_on = now_datetime()

        elif self.workflow_state == "Closed":
            self.status = "Closed"

            if not self.closed_on:
                self.closed_on = now_datetime()

        elif self.workflow_state == "Reopened":
            self.status = "Reopened"
            self.resolved_on = None