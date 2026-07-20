frappe.ui.form.on("Tickets Hd", {

    onload(frm) {

    setup_customer_ticket(frm);

    if (frm.is_new()) {
        if (!frm.doc.status) {
            frm.set_value("status", "Open");
        }
        if (!frm.doc.workflow_state) {
            frm.set_value("workflow_state", "Open");
        }
        if (frm.is_new() && frappe.user.has_role("HelpDesk Agent")) {
    frm.set_value("support_type", "Ad Hoc");
}
    }

    if (frappe.user.has_role("HelpDesk Agent")) {
        frm.set_query("project", function () {
            return {
                filters: {
                    support_type: "Ad Hoc"
                }
            };
        });
    }

},

    refresh(frm) {

        setup_customer_ticket(frm);
        show_workflow_message(frm);


        // CUSTOMER LOGIN


        if (frappe.user.has_role("HelpDesk Customer")) {

            frm.set_df_property("resolution_detail", "reqd", 0);

            // Read only fields
            [
                "customer",
                "support_type",
                "status",
                "assigned_agent",
                "assigned_on",
                "ticket_raised_by",
                "created_on",
                "resolved_on",
                "closed_on",
                "sla_policy",
                "first_response_due",
                "resolution_due",
                "sla_status",
                "first_responded_on",
                "response_breached",
                "resolution_breached"
            ].forEach(field => {
                frm.set_df_property(field, "read_only", 1);
            });

            if (frm.is_new()) {

                frm.toggle_display("assignment", false);
                frm.toggle_display("sla_tab", false);
                frm.toggle_display("resolution", false);

                frm.toggle_display("status", false);
                frm.toggle_display("assigned_agent", false);
                frm.toggle_display("assigned_on", false);
                frm.toggle_display("ticket_raised_by", false);

                frm.toggle_display("sla_policy", false);
                frm.toggle_display("first_response_due", false);
                frm.toggle_display("resolution_due", false);
                frm.toggle_display("sla_status", false);
                frm.toggle_display("first_responded_on", false);
                frm.toggle_display("escalation_due", false);
                frm.toggle_display("response_breached", false);
                frm.toggle_display("resolution_breached", false);

                frm.toggle_display("resolved_on", false);
                frm.toggle_display("closed_on", false);

                frm.toggle_display("resolution_detail", false);
                frm.toggle_display("customer_feedback", false);
                frm.toggle_display("reopen_reason", false);
                frm.toggle_display("communication", false);

            } else {

                frm.toggle_display("status", true);
                frm.toggle_display("assignment", true);
                frm.toggle_display("assigned_agent", true);
                frm.toggle_display("assigned_on", true);
                frm.toggle_display("communication", true);

                if (frm.doc.status === "Resolved" || frm.doc.status === "Closed") {
                    frm.toggle_display("resolution", true);
                    frm.toggle_display("customer_feedback", true);
                } else {
                    frm.toggle_display("customer_feedback", false);
                }

                if (frm.doc.status === "Reopened") {
                    frm.toggle_display("reopen_reason", true);
                } else {
                    frm.toggle_display("reopen_reason", false);
                }

            }

        }

        // AGENT LOGIN


        if (frappe.user.has_role("HelpDesk Agent")) {

    // Show button only for new Ad Hoc tickets
    if (frm.is_new() && frm.doc.support_type === "Ad Hoc") {

        frm.fields_dict.customer.$wrapper.find(".adhoc-btn").remove();

if (frm.is_new() && frm.doc.support_type === "Ad Hoc") {

    let btn = $(`
        <button class="btn btn-xs btn-default adhoc-btn" style="margin-top:6px;">
            + New Customer
        </button>
    `);

    btn.on("click", function () {
        open_adhoc_dialog(frm);
    });

frm.fields_dict.customer.$input_wrapper.append(btn);}

    }

    // Show resolution fields only for Resolved or Closed tickets
    if (frm.doc.status === "Resolved" || frm.doc.status === "Closed") {

        frm.toggle_display("resolution", true);
        frm.toggle_display("resolution_detail", true);
        frm.set_df_property("resolution_detail", "read_only", 0);
        frm.set_df_property("resolution_detail", "reqd", 1);

    } else {

        frm.toggle_display("resolution_detail", false);
        frm.set_df_property("resolution_detail", "reqd", 0);

    }

}

    },

    project(frm) {

        if (frappe.user.has_role("HelpDesk Customer") && frm.doc.project) {
            validate_project_support_period(frm);
        }

    },

    
    // VALIDATE AGENT RESOLUTION

    validate(frm) {

        if (frappe.user.has_role("HelpDesk Agent")) {
            if (frm.doc.status === "Resolved") {
                if (!frm.doc.resolution_detail) {
                    frappe.throw(
                        __("Please enter Resolution Details before resolving the ticket.")
                    );
                }
            }
        }

    },

    before_workflow_action: function (frm) {

    const action = frm.selected_workflow_action;

    if (action === "Reopen") {

        frappe.dom.unfreeze();

        return new Promise((resolve, reject) => {

            let dialog = new frappe.ui.Dialog({
                title: __("Reopen Ticket"),
                fields: [
                    {
                        label: __("Reopen Reason"),
                        fieldname: "reopen_reason",
                        fieldtype: "Small Text",
                        reqd: 1
                    }
                ],
                primary_action_label: __("Reopen"),
                primary_action(values) {

                    dialog.hide();

                    frappe.call({
                        method: "frappe.model.workflow.apply_workflow",
                        args: {
                            doc: frm.doc,
                            action: action
                        },
                        freeze: true,
                        callback: function (r) {

                            frappe.model.sync(r.message);

                            frappe.client.set_value(
                                "Tickets Hd",
                                frm.doc.name,
                                "reopen_reason",
                                values.reopen_reason
                            ).then(() => {
                                frm.reload_doc();
                            });

                        }
                    });

                },
                onhide() {
                    // Always reject — we handle the action ourselves above,
                    // this just stops Frappe's native handler from also firing.
                    reject();
                }
            });

            dialog.show();

        });

    }

    if (["Close", "Drop"].includes(action)) {

        frappe.dom.unfreeze();

        return new Promise((resolve, reject) => {

            frappe.confirm(
                __("Are you sure you want to " + action.toLowerCase() + " this ticket?"),
                () => {

                    frappe.call({
                        method: "frappe.model.workflow.apply_workflow",
                        args: {
                            doc: frm.doc,
                            action: action
                        },
                        freeze: true,
                        callback: function (r) {
                            frappe.model.sync(r.message);
                            frm.reload_doc();
                        }
                    });

                    reject(); // stop native handler from also applying the action
                },
                () => {
                    reject(); // "No" clicked — also just reject, nothing to apply
                }
            );

        });

    }

    return;

}

});


function setup_customer_ticket(frm) {

    if (!frappe.user.has_role("HelpDesk Customer")) {
        return;
    }

    frappe.db.get_value(
        "Customer hd",
        { portal_user: frappe.session.user },
        "name"
    ).then(r => {

        if (!r.message) {
            frappe.msgprint(__("Customer record not found."));
            return;
        }

        frm.set_value("customer", r.message.name);
        frm.set_df_property("customer", "read_only", 1);

        frm.set_query("project", function () {
            return {
                filters: {
                    customer: r.message.name
                }
            };
        });

    });

}


function show_workflow_message(frm) {

    // Skip if we've already shown the alert for this exact state
    if (frm.__last_alert_state === frm.doc.workflow_state) {
        return;
    }
    frm.__last_alert_state = frm.doc.workflow_state;

    switch (frm.doc.workflow_state) {

        case "Open":
            frappe.show_alert({ message: __("New ticket created."), indicator: "blue" });
            break;

        case "Assigned":
            frappe.show_alert({ message: __("Ticket Assigned"), indicator: "blue" });
            break;

        case "In progress":
            frappe.show_alert({ message: __("Support Team Working"), indicator: "orange" });
            break;

        case "Resolved":
            frappe.show_alert({ message: __("Waiting for Customer Confirmation"), indicator: "green" });
            break;

        case "Reopened":
            frappe.show_alert({ message: __("Ticket Reopened"), indicator: "red" });
            break;

        case "Closed":
            frappe.show_alert({ message: __("Ticket Closed"), indicator: "green" });
            break;

    }

}


function validate_project_support_period(frm) {

    if (!frm.doc.project) {
        return;
    }

    frappe.db.get_value(
        "Project hd",
        frm.doc.project,
        ["support_type", "end_date"]
    ).then(r => {

        if (!r.message) {
            return;
        }

        const support_type = r.message.support_type;
        const end_date = r.message.end_date;
        const today = frappe.datetime.get_today();

        // Ad Hoc projects are not allowed for customers
        if (support_type === "Ad Hoc") {

            frappe.msgprint({
                title: __("Ticket Not Allowed"),
                indicator: "red",
                message: __("This project is under Ad Hoc support. Customers cannot raise tickets.")
            });

            frm.set_value("project", "");
            return;
        }

        // Check expiry for AMC and Warranty
        if (["AMC", "Warranty"].includes(support_type) && end_date && end_date <= today) {

            frappe.msgprint({
                title: __("Support Period Expired"),
                indicator: "red",
                message: __(
                    "The {0} support period for this project expired on {1}. You cannot raise a new ticket. Please contact the agent.",
                    [support_type, frappe.datetime.str_to_user(end_date)]
                )
            });

            frm.set_value("project", "");

        }

    }).catch(error => {

        console.error("Unable to validate project support period:", error);

        frappe.msgprint(
            __("Unable to check the project support period. Please try again.")
        );

    });

}
function open_adhoc_dialog(frm) {

    let dialog = new frappe.ui.Dialog({
        title: __("Create Ad Hoc Customer"),
        fields: [
            {
                fieldname: "customer_name",
                label: "Customer Name",
                fieldtype: "Data",
                reqd: 1
            },
            {
                fieldname: "project_name",
                label: "Project Name",
                fieldtype: "Data",
                reqd: 1
            },
            {
                fieldname: "email_id",
                label: "Email",
                fieldtype: "Data"
            },
            {
                fieldname: "mobile_no",
                label: "Mobile",
                fieldtype: "Data"
            }
        ],

        primary_action_label: __("Create & Use"),

        primary_action(values) {

    frappe.call({
        method: "helpdesk_system.api.create_adhoc_customer_project",
        args: {
            data: values
        },

        freeze: true,
        freeze_message: __("Creating Customer & Project..."),

        callback: function(r) {

            if (!r.message) {
                return;
            }

            frm.set_value("customer", r.message.customer);
            frm.set_value("project", r.message.project);

            dialog.hide();

            frappe.show_alert({
                message: __("Customer & Project Created Successfully"),
                indicator: "green"
            });

        }

    });

}

    });

    dialog.show();

}