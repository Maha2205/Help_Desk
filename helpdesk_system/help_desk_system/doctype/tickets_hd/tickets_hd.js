frappe.ui.form.on("Tickets Hd", {

    onload: function(frm) {
        set_customer_for_portal_user(frm);
    },

    refresh: function(frm) {
        set_customer_for_portal_user(frm);

        const state = frm.doc.workflow_state;

        switch (state) {
            case "Open":
                frappe.show_alert({ message: __("New ticket created. Waiting for assignment."), indicator: "blue" });
                break;
            case "Assigned":
                frappe.show_alert({ message: __("Ticket has been assigned to a support agent."), indicator: "blue" });
                break;
            case "In Progress":
                frappe.show_alert({ message: __("Support team is currently working on this ticket."), indicator: "orange" });
                break;
            case "Resolved":
                frappe.show_alert({ message: __("Issue resolved. Waiting for customer confirmation."), indicator: "green" });
                break;
            case "Reopened":
                frappe.show_alert({ message: __("This ticket has been reopened."), indicator: "red" });
                break;
            case "Closed":
                frappe.show_alert({ message: __("Ticket closed successfully."), indicator: "green" });
                break;
            case "Dropped":
                frappe.show_alert({ message: __("This ticket has been dropped."), indicator: "gray" });
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
                frappe.confirm(message, () => resolve(true), () => resolve(false));
            });

            if (!confirmed) {
                frappe.throw(__("Workflow action cancelled."));
            }
        }
    }
});


function set_customer_for_portal_user(frm) {
    if (frappe.user.has_role("Helpdesk Customer")) {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Customer hd",
                filters: {
                    portal_user: frappe.session.user
                },
                fields: ["name"],
                limit_page_length: 1
            },
            callback: function(r) {
                if (r.message && r.message.length) {
                    frm.set_value("customer", r.message[0].name);
                    frm.set_df_property("customer", "read_only", 1);
                }
            }
        });
    }
}