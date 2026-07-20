frappe.after_ajax(() => {
    const roles = frappe.boot?.user?.roles || [];

    console.log("Roles:", roles);

    if (
        roles.includes("System Manager") ||
        roles.includes("HelpDesk Admin")
    ) {
        return;
    }

    if (
        roles.includes("HelpDesk Agent") ||
        roles.includes("HelpDesk Customer")
    ) {
        if (window.location.pathname !== "/desk/tickets-hd") {
            window.location.href = "/desk/tickets-hd";
        }
    }
});