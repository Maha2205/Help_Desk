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
                
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date


class TicketsHd(Document):

    def before_insert(self):
        self.set_sla_due_times()

    def before_save(self):
        self.set_first_response_time()
        self.set_resolution_time()
        self.update_sla_status()

    def set_sla_due_times(self):
        if not self.sla_policy:
            self.sla_policy = frappe.db.get_value(
                "SLA Policy",
                {"enabled": 1, "is_default": 1},
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
            ["first_response_time", "resolution_time"],
            as_dict=True
        )

        if not rule:
            return

        created_time = now_datetime()

        self.first_response_due_on = add_to_date(
            created_time,
            hours=rule.first_response_time
        )

        self.resolution_due_on = add_to_date(
            created_time,
            hours=rule.resolution_time
        )

        self.sla_status = "Within SLA"

    def set_first_response_time(self):
        if self.first_responded_on:
            return

        if self.assigned_agent and self.status in ["In Progress", "Resolved", "Closed"]:
            self.first_responded_on = now_datetime()

    def set_resolution_time(self):
        if self.status == "Resolved" and not self.resolved_on:
            self.resolved_on = now_datetime()

    def update_sla_status(self):
        current_time = now_datetime()

        if self.status == "Resolved":
            self.sla_status = "Completed"
            return

        if (
            self.first_response_due_on
            and not self.first_responded_on
            and current_time > self.first_response_due_on
        ):
            self.sla_status = "First Response Breached"
            return

        if (
            self.resolution_due_on
            and current_time > self.resolution_due_on
        ):
            self.sla_status = "Resolution Breached"
            return

        self.sla_status = "Within SLA"