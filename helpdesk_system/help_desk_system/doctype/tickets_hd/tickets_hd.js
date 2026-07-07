// Copyright (c) 2026, mahalakshmi and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Tickets Hd", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Tickets Hd", {

    onload: function(frm) {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Customer hd",
                filters: {
                    user: frappe.session.user
                },
                fields: ["name"],
                limit_page_length: 1
            },
            callback: function(r) {
                if (r.message.length) {
                    frm.set_value("customer", r.message[0].name);
                }
            }
        });
    },

    refresh: function(frm) {

        const state = frm.doc.workflow_state;

        switch (state) {

            case "Open":
                frappe.show_alert({
                    message: __("New ticket created. Waiting for assignment."),
                    indicator: "blue"
                });
                break;

            case "Assigned":
                frappe.show_alert({
                    message: __("Ticket has been assigned to a support agent."),
                    indicator: "blue"
                });
                break;

            case "In Progress":
                frappe.show_alert({
                    message: __("Support team is currently working on this ticket."),
                    indicator: "orange"
                });
                break;

            case "Resolved":
                frappe.show_alert({
                    message: __("Issue resolved. Waiting for customer confirmation."),
                    indicator: "green"
                });
                break;

            case "Reopened":
                frappe.show_alert({
                    message: __("This ticket has been reopened."),
                    indicator: "red"
                });
                break;

            case "Closed":
                frappe.show_alert({
                    message: __("Ticket closed successfully."),
                    indicator: "green"
                });
                break;

            case "Dropped":
                frappe.show_alert({
                    message: __("This ticket has been dropped."),
                    indicator: "gray"
                });
                break;
        }
    },

    before_workflow_action: async function(frm) {

        const action = frm.selected_workflow_action;

        if (["Close", "Reopen"].includes(action)) {

            const message = action === "Close"
                ? __("Are you sure you want to close this ticket?")
                : __("Are you sure you want to reopen this ticket?");

            const confirmed = await new Promise((resolve) => {
                frappe.confirm(
                    message,
                    () => resolve(true),
                    () => resolve(false)
                );
            });

            if (!confirmed) {
                frappe.throw(__("Workflow action cancelled."));
            }
        }
    }

});