frappe.ui.form.on("Sales Invoice", {
    on_submit: function(frm) {
        if (frm.doc.mode_of_payment_a_001 === "نقداً" || frm.doc.mode_of_payment_a_001 === "فيزا") {
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



// --------  Purchase Receipt Doctype that opens a dialog to add batch numbers manually or via CSV  ---------





frappe.ui.form.on('Purchase Receipt', {
    onload: function (frm) {
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




//  ---------------------------------------





//
//frappe.ui.form.on('Purchase Receipt', {
//    onload: function (frm) {
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
//                ],
//                primary_action_label: __('Save'),
//                primary_action(values) {
//                    if (!values.entries || values.entries.length === 0) {
//                        frappe.msgprint(__('Please add at least one row to the Batch Details table.'));
//                        return;
//                    }
//
//                    frappe.call({
//                        method: 'payment_entry_test_001.payment_entry_test_001.payment_entry_py.add_batch_to_doctype',
//                        args: {
//                            batch_details: JSON.stringify(values.entries),
//                            item_code: values.item_code,
//                            warehouse: values.warehouse
//                        },
//
//                        callback: function (r) {
//                            if (r.message) {
//                                frappe.msgprint(__('Batch Details Saved'));
//                                frappe.call({
//                                    method: 'payment_entry_test_001.payment_entry_test_001.payment_entry_py.add_to_serial_and_batch_bundle',
//                                    args: {
//                                        batch_details: JSON.stringify(values.entries),
//                                        item_code: values.item_code,
//                                        warehouse: values.warehouse,
//                                        purchase_receipt: frm.doc.name
//                                    },
//                                    callback: function (r) {
//                                        if (r.message) {
//                                            frappe.msgprint(__('Serial and Batch Bundle Added'));
//                                            dialog.hide();
//                                            frm.reload_doc();
//                                        }
//                                    }
//                                });
//                            }
//                        }
//
//                    });
//                }
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


//  ---------------------------------------






//  ---------------------------------------

//frappe.ui.form.on('Purchase Receipt', {
//    onload: function (frm) {
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
//                ],
//                primary_action_label: __('Save'),
//
//                primary_action(values) {
//                    if (!values.entries || values.entries.length === 0) {
//                        frappe.msgprint(__('Please add at least one row to the Batch Details table.'));
//                        return;
//                    }
//
//                    frappe.call({
//                        method: 'payment_entry_test_001.payment_entry_test_001.payment_entry_py.save_batch_details',
//                        args: {
//                            batch_details: JSON.stringify(values.entries),
//                            item_code: values.item_code,
//                            warehouse: values.warehouse,
//                            purchase_receipt: frm.doc.name
//                        },
//                        callback: function (r) {
//                            if (r.message) {
//                                frappe.msgprint(__('Batch Details Saved'));
//                                dialog.hide();
//                                frm.reload_doc();
//                            }
//                        }
//                    });
//                }
//
//
//
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

//  ---------------------------------------



//  ---------------------------------------
//frappe.ui.form.on('Purchase Receipt', {
//    onload: function (frm) {
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
//                        label: __('Batch No'),
//                        fieldname: 'batch_no',
//                        fieldtype: 'Data',
//                        hidden: 0,
//                        reqd: 0
//                    },
//                    {
//                        label: __('Quantity'),
//                        fieldname: 'quantity',
//                        fieldtype: 'Float',
//                        hidden: 0,
//                        reqd: 0
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
//                ],
//                primary_action_label: __('Save'),
//                primary_action(values) {
//                    frappe.call({
//                        method: 'payment_entry_test_001.payment_entry_test_001.payment_entry_py.save_batch_details',
//                        args: {
//                            batch_details: values.entries,
//                            item_code: values.item_code,
//                            warehouse: values.warehouse
//                        },
//                        callback: function (r) {
//                            if (r.message) {
//                                frappe.msgprint(__('Batch Details Saved'));
//                                dialog.hide();
//                                frm.reload_doc();
//                            }
//                        }
//                    });
//                }
//            });
//
//            dialog.fields_dict.batch_no.$input.on('keypress', function (e) {
//                if (e.key === 'Enter') {
//                    const batch_no = dialog.get_value('batch_no');
//                    const quantity = dialog.get_value('quantity');
//                    if (batch_no && quantity) {
//                        dialog.fields_dict.entries.df.data.push({
//                            batch_no,
//                            quantity
//                        });
//                        dialog.fields_dict.entries.grid.refresh();
//                        dialog.set_value('batch_no', '');
//                        dialog.set_value('quantity', '');
//                    }
//                }
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






// ==============================================
// ==============================================
