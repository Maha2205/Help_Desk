// Copyright (c) 2026, mahalakshmi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tickets Hd", {
	refresh(frm) {

	},

    onload: function(frm) {
        if(frm.is_new() && frappe.session.user != "Administrator"){
            _get_customer(frm);
        }
    },
});

function _get_customer(frm){
    customer = frappe.db.get_value("Customer hd", {"email_id": frappe.session.user}, "name").then(r => {
        if(r.message){
            
            frm.set_value("customer", r.message.name);
            frm.set_df_property("customer", "read_only", 1); 
        }
    });
}

