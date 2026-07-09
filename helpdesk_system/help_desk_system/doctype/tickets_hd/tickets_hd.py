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