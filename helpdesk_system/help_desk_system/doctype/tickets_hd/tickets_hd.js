frappe.ui.form.on("Tickets Hd", {

    onload(frm) {

        setup_customer_ticket(frm);

        // Show only Ad Hoc projects for HelpDesk Agent
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



        // ==========================
        // CUSTOMER LOGIN
        // ==========================

        if (frappe.user.has_role("HelpDesk Customer")) {


            frm.set_df_property(
                "resolution_detail",
                "reqd",
                0
            );


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

                frm.set_df_property(
                    field,
                    "read_only",
                    1
                );

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



                if (
                    frm.doc.status === "Resolved" ||
                    frm.doc.status === "Closed"
                ) {


                    frm.toggle_display(
                        "resolution",
                        true
                    );


                    frm.toggle_display(
                        "customer_feedback",
                        true
                    );


                } else {


                    frm.toggle_display(
                        "customer_feedback",
                        false
                    );


                }



                if (frm.doc.status === "Reopened") {


                    frm.toggle_display(
                        "reopen_reason",
                        true
                    );


                } else {


                    frm.toggle_display(
                        "reopen_reason",
                        false
                    );


                }

            }

        }



        // ==========================
        // AGENT LOGIN
        // ==========================

        if (frappe.user.has_role("HelpDesk Agent")) {


            if (
                frm.doc.status === "Resolved" ||
                frm.doc.status === "Closed"
            ) {


                frm.toggle_display(
                    "resolution",
                    true
                );


                frm.toggle_display(
                    "resolution_detail",
                    true
                );


                frm.set_df_property(
                    "resolution_detail",
                    "read_only",
                    0
                );


                frm.set_df_property(
                    "resolution_detail",
                    "reqd",
                    1
                );


            } else {


                frm.toggle_display(
                    "resolution_detail",
                    false
                );


                frm.set_df_property(
                    "resolution_detail",
                    "reqd",
                    0
                );


            }

        }

    },



    // ==========================
    // VALIDATE AGENT RESOLUTION
    // ==========================

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


//bv//
});





function setup_customer_ticket(frm) {


    if (!frappe.user.has_role("HelpDesk Customer")) {

        return;

    }



    frappe.db.get_value(

        "Customer hd",

        {
            portal_user: frappe.session.user
        },

        "name"

    ).then(r => {



        if (!r.message) {


            frappe.msgprint(
                __("Customer record not found.")
            );


            return;


        }



        frm.set_value(
            "customer",
            r.message.name
        );



        frm.set_df_property(
            "customer",
            "read_only",
            1
        );



        frm.set_query(
            "project",
            function () {

                return {

                    filters: {

                        customer: r.message.name

                    }

                };

            }

        );


    });


}





function show_workflow_message(frm) {


    switch (frm.doc.workflow_state) {


        case "Open":

            frappe.show_alert({

                message: __("New ticket created."),

                indicator: "blue"

            });

            break;



        case "Assigned":

            frappe.show_alert({

                message: __("Ticket Assigned"),

                indicator: "blue"

            });

            break;



        case "In Progress":

            frappe.show_alert({

                message: __("Support Team Working"),

                indicator: "orange"

            });

            break;



        case "Resolved":

            frappe.show_alert({

                message: __("Waiting for Customer Confirmation"),

                indicator: "green"

            });

            break;



        case "Reopened":

            frappe.show_alert({

                message: __("Ticket Reopened"),

                indicator: "red"

            });

            break;



        case "Closed":

            frappe.show_alert({

                message: __("Ticket Closed"),

                indicator: "green"

            });

            break;


    }

}