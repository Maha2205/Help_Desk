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
    }
});
