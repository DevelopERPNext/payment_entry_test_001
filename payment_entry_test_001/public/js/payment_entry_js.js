frappe.ui.form.on("Sales Invoice", {
    onload: function(frm) {
        if (frm.doc.docstatus === 0) {
//        if (frm.doc.docstatus === 0 && frm.doc.stock_entry_type === 'Manufacture' && frm.doc.bom_check === 1) {
            frm.add_custom_button(__('Payment Entry Test 001'), function() {
                frappe.call({
                    method: "payment_entry_test_001.payment_entry_test_001.payment_entry_py.create_print_msg",
                    args: {
                        "doc": frm.doc.name,
                    },
                    callback: function(response) {
                        if (response.message) {
                            frappe.show_alert({
                                message: __(response.message),
                                indicator: 'green'
                            });
                            frm.reload_doc();
                            // frm.refresh();
                        }
                        frm.reload_doc();
                    }
                });
            }).addClass('btn-warning').css({
                'color': 'white',
                'font-weight': 'bold',
                'background-color': '#274472'
            });
        }
    },
});


// ==============================================
// ==============================================