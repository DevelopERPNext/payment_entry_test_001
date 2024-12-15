frappe.ui.form.on("Sales Invoice", {
    on_submit: function(frm) {
        if (frm.doc.mode_of_payment_a_001 === "نقداً" || frm.doc.mode_of_payment_a_001 === "فيزا") {
            frm.reload_doc();
        }
    }
});



// =========================================



frappe.ui.form.on("Sales Invoice", {
    on_submit: function(frm) {
        if (frm.doc.select_sales_transactions_a_001 === "مبيعات نقدية") {
            frm.reload_doc();
        }
    }
});



// =========================================




//frappe.ui.form.on("Sales Invoice", {
//    onload: function(frm) {
//        if (frm.doc.docstatus === 0) {
////        if (frm.doc.docstatus === 0 && frm.doc.stock_entry_type === 'Manufacture' && frm.doc.bom_check === 1) {
//            frm.add_custom_button(__('Payment Entry Test 001'), function() {
//                frappe.call({
//                    method: "payment_entry_test_001.payment_entry_test_001.payment_entry_py.create_print_msg",
//                    args: {
//                        "doc": frm.doc.name,
//                    },
//                    callback: function(response) {
//                        if (response.message) {
//                            frappe.show_alert({
//                                message: __(response.message),
//                                indicator: 'green'
//                            });
//                            frm.reload_doc();
//                            // frm.refresh();
//                        }
//                        frm.reload_doc();
//                    }
//                });
//            }).addClass('btn-warning').css({
//                'color': 'white',
//                'font-weight': 'bold',
//                'background-color': '#274472'
//            });
//        }
//    },
//});




// ==============================================
// ==============================================



// -------- START Purchase Receipt Doctype that opens a dialog to add batch numbers manually or via CSV  ---------



// payment_entry_test_001.payment_entry_test_001.payment_entry_py.

//  dialog.get_primary_btn().hide();


frappe.ui.form.on('Purchase Receipt', {
    onload: function (frm) {

        if (frm.doc.docstatus === 1) {
            return;
        }
        frm.add_custom_button(__('Add Batch Nos'), () => {
            const items = frm.doc.items || [];
            if (items.length === 0) {
                frappe.msgprint(__('Please add items to the Purchase Receipt before adding batch numbers.'));
                return;
            }

            const dialog = new frappe.ui.Dialog({
                title: __('Add Batch Numbers'),
                fields: [
                    {
                        label: __('Item Code'),
                        fieldname: 'item_code',
                        fieldtype: 'Select',
                        options: items.map((item) => item.item_code),
                        reqd: 1,
                        onchange: function () {
                            const selected_item_code = dialog.get_value('item_code');
                            const selected_item = items.find((item) => item.item_code === selected_item_code);
                            if (selected_item) {
                                dialog.set_value('warehouse', selected_item.warehouse);
                            }
                        }
                    },
                    {
                        label: __('Warehouse'),
                        fieldname: 'warehouse',
                        fieldtype: 'Link',
                        options: 'Warehouse',
                        reqd: 1,
                        read_only: 1
                    },
                    {
                        fieldtype: 'Table',
                        fieldname: 'entries',
                        label: __('Batch Details'),
                        fields: [
                            {
                                fieldname: 'batch_no',
                                label: __('Batch No'),
                                fieldtype: 'Data',
                                in_list_view: 1,
                                reqd: 1
                            },
                            {
                                fieldname: 'quantity',
                                label: __('Quantity'),
                                fieldtype: 'Float',
                                in_list_view: 1,
                                reqd: 1
                            }
                        ],
                        data: [],
                        cannot_add_rows: false
                    }
                ],
                primary_action_label: __('Save'),
                primary_action(values) {
                    if (!values.entries || values.entries.length === 0) {
                        frappe.msgprint(__('Please add at least one row to the Batch Details table.'));
                        return;
                    }

                    frappe.call({
                        method: 'payment_entry_test_001.payment_entry_test_001.payment_entry_py.save_batch_details',
                        args: {
                            batch_details: JSON.stringify(values.entries),
                            item_code: values.item_code,
                            warehouse: values.warehouse,
                            purchase_receipt: frm.doc.name
                        },
                        callback: function (r) {
                            if (r.message) {
//                                frappe.msgprint(__('Batch Details Saved'));

                                frappe.show_alert({
                                    message: __('Batch Details Saved'),
                                    indicator: 'green'
                                });
                                dialog.hide();
                                frm.reload_doc();
                            }
                        }
                    });
                }
            });

            dialog.show();
        }).addClass('btn-warning').css({
            'color': 'white',
            'font-weight': 'bold',
            'background-color': '#274472'
        });
    }
});





// -------------------------------------------



//frappe.ui.form.on('Purchase Receipt', {
//    refresh: function (frm) {
//        frm.add_custom_button(__('Add Batch Nos'), () => {
//            const items = frm.doc.items || [];
//            if (items.length === 0) {
//                frappe.msgprint(__('Please add items to the Purchase Receipt before adding batch numbers.'));
//                return;
//            }
//
//            const dialog = new frappe.ui.Dialog({
//                title: __('Add Batch Numbers'),
//                fields: [
//                    {
//                        label: __('Item Code'),
//                        fieldname: 'item_code',
//                        fieldtype: 'Select',
//                        options: items.map((item) => item.item_code),
//                        reqd: 1,
//                        onchange: function () {
//                            const selected_item_code = dialog.get_value('item_code');
//                            const selected_item = items.find((item) => item.item_code === selected_item_code);
//                            if (selected_item) {
//                                dialog.set_value('warehouse', selected_item.warehouse);
//                            }
//                        }
//                    },
//                    {
//                        label: __('Warehouse'),
//                        fieldname: 'warehouse',
//                        fieldtype: 'Link',
//                        options: 'Warehouse',
//                        reqd: 1,
//                        read_only: 1
//                    },
//                    {
//                        fieldtype: 'Table',
//                        fieldname: 'entries',
//                        label: __('Batch Details'),
//                        fields: [
//                            {
//                                fieldname: 'batch_no',
//                                label: __('Batch No'),
//                                fieldtype: 'Data',
//                                in_list_view: 1,
//                                reqd: 1
//                            },
//                            {
//                                fieldname: 'quantity',
//                                label: __('Quantity'),
//                                fieldtype: 'Float',
//                                in_list_view: 1,
//                                reqd: 1
//                            }
//                        ],
//                        data: [],
//                        cannot_add_rows: false
//                    }
//                ]
//            });
//
//            dialog.set_primary_action(__('Save'), function () {
//                const values = dialog.get_values();
//                if (!values.entries || values.entries.length === 0) {
//                    frappe.msgprint(__('Please add at least one row to the Batch Details table.'));
//                    return;
//                }
//
//                frappe.call({
//                    method: 'payment_entry_test_001.payment_entry_test_001.payment_entry_py.add_batches',
//                    args: {
//                        batch_details: JSON.stringify(values.entries),
//                        item_code: values.item_code,
//                        warehouse: values.warehouse,
//                        purchase_receipt: frm.doc.name
//                    },
//                    callback: function (r) {
//                        if (r.message) {
//                            frappe.show_alert({
//                                message: __('Batch Details Saved'),
//                                indicator: 'green'
//                            });
//                            dialog.get_primary_btn().hide();
//                        }
//                    }
//                });
//            });
//
//            dialog.footer.append(`
//                <button class="btn btn-secondary btn-sm add-serial-bundle-btn" style="margin-left: 10px;">
//                    ${__('Add Serial and Batch Bundle')}
//                </button>
//            `);
//
//            dialog.$wrapper.find('.add-serial-bundle-btn').on('click', function () {
//                const values = dialog.get_values();
//                frappe.call({
//                    method: 'payment_entry_test_001.payment_entry_test_001.payment_entry_py.create_serial_and_batch_bundle',
//                    args: {
//                        batch_details: JSON.stringify(values.entries),
//                        item_code: values.item_code,
//                        warehouse: values.warehouse,
//                        purchase_receipt: frm.doc.name
//                    },
//                    callback: function (res) {
//                        if (res.message) {
//                            frm.doc.items.forEach((item) => {
//                                if (item.item_code === values.item_code) {
//                                    item.serial_and_batch_bundle = res.message;
//                                }
//                            });
//                            frm.refresh_field('items');
//                            frappe.show_alert({
//                                message: __('Serial and Batch Bundle Created'),
//                                indicator: 'green'
//                            });
//                            dialog.hide();
//                            frm.reload_doc();
//                        }
//                    }
//                });
//            });
//
//            dialog.show();
//        }).addClass('btn-warning').css({
//            'color': 'white',
//            'font-weight': 'bold',
//            'background-color': '#274472'
//        });
//    }
//});

// -------------------------------------------


// -------- END Purchase Receipt Doctype that opens a dialog to add batch numbers manually or via CSV  ---------



// ==============================================
// ==============================================









// ==============================================
// ==============================================



// -------- START Define the naming series mapping based on voucher_type ---------



frappe.ui.form.on('Journal Entry', {
//    voucher_type: function(frm) {
    validate: function(frm) {
        let namingSeriesMapping = {
            "Journal Entry": "ACC-JV-.YYYY.-",
            "Inter Company Journal Entry": "ACC-ICJE-.YYYY.-",
            "Bank Entry": "ACC-BE-.YYYY.-",
            "Cash Entry": "ACC-CE-.YYYY.-",
            "Credit Card Entry": "ACC-CCE-.YYYY.-",
            "Debit Note": "ACC-DN-.YYYY.-",
            "Credit Note": "ACC-CN-.YYYY.-",
            "Contra Entry": "ACC-COE-.YYYY.-",
            "Excise Entry": "ACC-EE-.YYYY.-",
            "Write Off Entry": "ACC-WOE-.YYYY.-",
            "Opening Entry": "ACC-OE-.YYYY.-",
            "Depreciation Entry": "ACC-DE-.YYYY.-",
            "Exchange Rate Revaluation": "ACC-ERR-.YYYY.-",
            "Exchange Gain Or Loss": "ACC-EGL-.YYYY.-",
            "Deferred Revenue": "ACC-DR-.YYYY.-",
            "Deferred Expense": "ACC-DEE-.YYYY.-"
        };

        if (frm.doc.voucher_type && namingSeriesMapping[frm.doc.voucher_type]) {
            frm.set_value('naming_series', namingSeriesMapping[frm.doc.voucher_type]);
        } else {
            frm.set_value('naming_series', 'ACC-JV-.YYYY.-');
        }
    },


//    refresh: function(frm) {
//        if (frm.doc.voucher_type) {
//            frm.trigger('voucher_type');
//        }
//    }


});




// -------- END  Define the naming series mapping based on voucher_type  ---------


















// ==============================================
// ==============================================



// -------- START Fetch the default branch from Session Defaults On Doctype "Sales Invoice" ---------



frappe.ui.form.on('Sales Invoice', {
    onload: function(frm) {
        frappe.db.get_value('Sales Invoice', frm.doc.name, 'branch_link_mode_of_payment_a_002', (r) => {
            if (r && r.branch_link_mode_of_payment_a_002) {
                frm.set_value('branch_link_mode_of_payment_a_002', r.branch_link_mode_of_payment_a_002);
            } else {
                let default_branch = frappe.defaults.get_default('branch');
                if (default_branch) {
                    frm.set_value('branch_link_mode_of_payment_a_002', default_branch);
                }
            }
        });
    }
});





//frappe.ui.form.on('Sales Invoice', {
//    onload: function(frm) {
//        let default_branch = frappe.defaults.get_default('branch');
//        if (default_branch) {
//            frm.set_value('branch_link_mode_of_payment_a_002', default_branch);
//        }
//    }
//});



// -------- END Fetch the default branch from Session Defaults On Doctype "Sales Invoice" ---------




// ==============================================
// ==============================================












// ==============================================
// ==============================================



// -------- START Fetch the selectable options based on the value of data_check_purchase_transactions_a_001 in the Purchase Invoice ---------


frappe.ui.form.on('Purchase Invoice', {
    refresh: function (frm) {
        frappe.call({
            method: "payment_entry_test_001.payment_entry_test_001.payment_entry_py.get_all_child_table_values",
            args: {
                doc: frm.doc.name
            },
            callback: function (r) {
                if (r.message) {
                    let options = r.message.join("\n");

//                    frappe.msgprint("test -----------------");
//                    frappe.msgprint(options);

                        frm.set_query("select_account_purchase_invoice_for_table_items_aa_001", function () {
                        let options = frm.fields_dict.select_account_purchase_invoice_for_table_items_a_001.df.options;
                        if (options) {
                            return {
                                filters: {
                                    name: ["in", options.split("\n")]
                                }
                            };
                        }
                    });

                    frm.set_df_property(
                        "select_account_purchase_invoice_for_table_items_aa_001",
                        "options",
                        options
                    );

                    frm.refresh_field("select_account_purchase_invoice_for_table_items_aa_001");
                } else {
                    frappe.msgprint("No options returned from the server.");
                }
            }
        });
    }
});


// -------- END Fetch the selectable options based on the value of data_check_purchase_transactions_a_001 in the Purchase Invoice ---------




// ==============================================
// ==============================================








// =========================================


frappe.ui.form.on("Sales Invoice", {
    validate: function(frm) {
        if (frm.doc.is_return === 1) {
            frm.set_value('data_check_sales_transactions_a_001', 0);

            if (frm.doc.data_check_sales_transactions_a_001 === 1) {
                frm.reload_doc();
            }

        }
        else {

        }
    },
});


// =========================================





// =========================================


frappe.ui.form.on("Purchase Invoice", {
    validate: function(frm) {
        if (frm.doc.is_return === 1) {
            frm.set_value('data_check_purchase_transactions_a_001', 0);

            if (frm.doc.data_check_purchase_transactions_a_001 === 1) {
                frm.reload_doc();
            }

        }
        else {

        }
    },
});


// =========================================

















// ==============================================
// ==============================================








// ==============================================
// ==============================================









// ==============================================
// ==============================================








// ==============================================
// ==============================================








// ==============================================
// ==============================================












// ==============================================
// ==============================================
// ==============================================
// ==============================================

