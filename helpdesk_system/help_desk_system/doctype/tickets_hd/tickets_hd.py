import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


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
        self.validate_ad_hoc_project()
        self.sync_status_with_workflow()

    def validate_ad_hoc_project(self):
        if not self.project:
            return

        support_type = frappe.db.get_value(
            "Project hd",
            self.project,
            "support_type"
        )

        customer_user = frappe.db.get_value(
            "Customer hd",
            self.customer,
            "portal_user"
        )

        if frappe.session.user == customer_user and support_type == "Ad Hoc":
            frappe.throw(
                "This project is under Ad Hoc support. "
                "Customers cannot raise tickets."
            )

    def sync_status_with_workflow(self):

        if self.workflow_state == "Assigned":
            self.status = "Assigned"

            if not self.first_responded_on:
                self.first_responded_on = now_datetime()

        elif self.workflow_state == "In Progress":
            self.status = "In Progress"

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