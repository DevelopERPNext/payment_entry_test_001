# Copyright (c) 2024, Mahmoud Khattab
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

from frappe.utils import nowdate


import json
from frappe.utils import flt

from frappe.exceptions import ValidationError


@frappe.whitelist()
def create_print_msg(doc, method=None):
    frappe.msgprint(str("Payment Entry Test 001 has been created."), alert=True)
    # doc.reload()

    # sales_invoice = doc
    #
    # if sales_invoice.mode_of_payment_a_001 == "نقداً":
    #     mode_of_payment_doc = frappe.get_value("Company", sales_invoice.company, "default_cash_account")
    #     mode_of_payment_doc_C = frappe.db.get_single_value(
    #         "payment_entry_test_0002",
    #         "default_cash_account_payment_a_001"
    #     )
    #
    #     frappe.msgprint(str(mode_of_payment_doc))
    #     frappe.msgprint(str(mode_of_payment_doc_C))


@frappe.whitelist()
def create_payment_entry_from_sales_invoice(doc, method=None):
    """
        create payment entry from sales invoice

        """

    try:
        # if isinstance(doc, str):
        #     sales_invoice = frappe.get_doc("Sales Invoice", doc)

        sales_invoice = doc

        # frappe.msgprint(str(sales_invoice))

        if not sales_invoice.mode_of_payment_a_001:
            pass
        else:
            # Create Payment Entry
            payment_entry = frappe.new_doc("Payment Entry")
            payment_entry.payment_type = "Receive"
            payment_entry.party_type = "Customer"
            payment_entry.party = sales_invoice.customer
            payment_entry.posting_date = nowdate()
            payment_entry.company = sales_invoice.company
            payment_entry.mode_of_payment = sales_invoice.mode_of_payment_a_001
            payment_entry.paid_amount = sales_invoice.outstanding_amount
            payment_entry.received_amount = sales_invoice.outstanding_amount
            payment_entry.reference_no = sales_invoice.name
            payment_entry.reference_date = sales_invoice.posting_date

            if sales_invoice.currency != sales_invoice.company_currency:
                exchange_rate = frappe.get_value('Currency Exchange', {
                    'from_currency': sales_invoice.currency,
                    'to_currency': sales_invoice.company_currency,
                    'transaction_date': sales_invoice.posting_date
                }, 'exchange_rate')

                if not exchange_rate:
                    frappe.throw(
                        f"Exchange rate not found for {sales_invoice.currency} to {sales_invoice.company_currency}.")

                payment_entry.target_exchange_rate = exchange_rate
            else:
                payment_entry.target_exchange_rate = 1

            bank_account = frappe.get_value("Company", doc.company,
                                            "default_receivable_account")

            if not bank_account:
                frappe.throw("Bank Account is not set for the company.")

            if sales_invoice.mode_of_payment_a_001 == "نقداً":
                # mode_of_payment_doc = frappe.get_value("Company", sales_invoice.company, "default_cash_account")

                mode_of_payment_doc = frappe.db.get_single_value(
                    "payment_entry_test_0002",
                    "default_cash_account_payment_a_001"
                )

            else:
                # mode_of_payment_doc = frappe.get_doc('Mode of Payment Account',
                #                                      {'parent': sales_invoice.mode_of_payment_a_001})

                mode_of_payment_doc = frappe.db.get_single_value(
                    "payment_entry_test_0002",
                    "default_visa_account_payment_a_001"
                )

            payment_entry.paid_to = mode_of_payment_doc
            payment_entry.paid_to_account_currency = sales_invoice.company_currency


            # Add the reference to the Sales Invoice
            payment_entry.append("references", {
                "reference_doctype": "Sales Invoice",
                "reference_name": sales_invoice,
                "total_amount": sales_invoice.grand_total,
                "outstanding_amount": sales_invoice.outstanding_amount,
                "allocated_amount": sales_invoice.outstanding_amount
            })

            # Save and Submit the Payment Entry
            payment_entry.insert(ignore_permissions=True)
            payment_entry.submit()

            # Link the Payment Entry
            if "payments" in sales_invoice.meta.get_table_fields():
                sales_invoice.append("payments", {
                    "payment_entry": payment_entry.name,
                    "amount": sales_invoice.outstanding_amount
                })
                sales_invoice.save()

            frappe.msgprint(
                f"Payment Entry {payment_entry.name} has been created and linked to Sales Invoice {sales_invoice}.",
                alert=True
            )

            return payment_entry.name

            sales_invoice.reload()

    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="Payment Entry Creation Error")
        frappe.throw(f"Error creating Payment Entry: {str(e)}")








#  ==============================================================




# -------- START Purchase Receipt Doctype that opens a dialog to add batch numbers manually or via CSV  ---------

@frappe.whitelist()
def save_batch_details(batch_details, item_code, warehouse, purchase_receipt):
    import json

    batch_details = json.loads(batch_details)
    purchase_receipt_doc = frappe.get_doc("Purchase Receipt", purchase_receipt)

    item_qty = next((item.qty for item in purchase_receipt_doc.items if item.item_code == item_code), None)
    if item_qty is None:
        frappe.throw(f"Item {item_code} not found in the Purchase Receipt.")

    total_batch_qty = sum([float(detail.get("quantity", 0)) for detail in batch_details])
    if total_batch_qty != item_qty:
        frappe.throw(f"Total batch quantity ({total_batch_qty}) does not match item quantity ({item_qty}) for item {item_code} in Purchase Receipt {purchase_receipt}.")

    for detail in batch_details:
        batch_no = detail.get("batch_no")
        quantity = detail.get("quantity")

        if batch_no and quantity:
            if not frappe.db.exists("Batch", batch_no):
                batch = frappe.get_doc({
                    "doctype": "Batch",
                    "batch_id": batch_no,
                    "item": item_code,
                    "warehouse": warehouse
                })
                batch.insert()
            else:
                batch = frappe.get_doc("Batch", batch_no)

            batch.batch_qty = (batch.batch_qty or 0) + float(quantity)
            batch.save()

    bundle_doc = frappe.get_doc({
        "doctype": "Serial and Batch Bundle",
        "item_code": item_code,
        "warehouse": warehouse,
        "type_of_transaction": "Inward",
        "voucher_type": "Purchase Receipt",
        "voucher_no": purchase_receipt,
        "entries": []
    })

    for detail in batch_details:
        batch_no = detail.get("batch_no")
        quantity = detail.get("quantity")
        if batch_no and quantity:
            bundle_doc.append("entries", {
                "batch_no": batch_no,
                "qty": quantity
            })

    bundle_doc.title = f"{item_code} - {purchase_receipt}"

    bundle_total_qty = sum([entry.get("qty", 0) for entry in bundle_doc.entries])
    if bundle_total_qty != item_qty:
        frappe.throw(f"Total quantity in the bundle ({bundle_total_qty}) does not match the item quantity ({item_qty}) in the Purchase Receipt.")

    bundle_doc.insert(ignore_permissions=True)

    for item in purchase_receipt_doc.items:
        if item.item_code == item_code:
            item.serial_and_batch_bundle = bundle_doc.name

    purchase_receipt_doc.save()
    frappe.db.commit()
    return "Success"




#  --------------------------------------




# @frappe.whitelist()
# def add_batches(batch_details, item_code, warehouse, purchase_receipt):
#     import json
#
#     batch_details = json.loads(batch_details)
#     purchase_receipt_doc = frappe.get_doc("Purchase Receipt", purchase_receipt)
#
#     item_qty = next((item.qty for item in purchase_receipt_doc.items if item.item_code == item_code), None)
#     if item_qty is None:
#         frappe.throw(f"Item {item_code} not found in the Purchase Receipt.")
#
#     total_batch_qty = sum(detail.get("quantity", 0) for detail in batch_details)
#     if total_batch_qty > item_qty:
#         frappe.throw(f"Total batch quantity ({total_batch_qty}) exceeds item quantity ({item_qty}) for item {item_code} in Purchase Receipt {purchase_receipt}.")
#
#     for detail in batch_details:
#         batch_no = detail.get("batch_no")
#         quantity = detail.get("quantity")
#
#         if batch_no and quantity:
#             if not frappe.db.exists("Batch", batch_no):
#                 batch = frappe.get_doc({
#                     "doctype": "Batch",
#                     "batch_id": batch_no,
#                     "item": item_code,
#                     "warehouse": warehouse
#                 })
#                 batch.insert()
#             else:
#                 batch = frappe.get_doc("Batch", batch_no)
#
#             batch.batch_qty = (batch.batch_qty or 0) + float(quantity)
#             batch.save()
#
#     frappe.db.commit()
#     return "Batches Added Successfully"
#
#
#
# @frappe.whitelist()
# def create_serial_and_batch_bundle(batch_details, item_code, warehouse, purchase_receipt):
#     import json
#
#     batch_details = json.loads(batch_details)
#     purchase_receipt_doc = frappe.get_doc("Purchase Receipt", purchase_receipt)
#
#     item_qty = next((item.qty for item in purchase_receipt_doc.items if item.item_code == item_code), None)
#     if item_qty is None:
#         frappe.throw(f"Item {item_code} not found in the Purchase Receipt.")
#
#     total_batch_quantity = sum([detail.get("quantity", 0) for detail in batch_details])
#     if total_batch_quantity != item_qty:
#         frappe.throw(f"Total quantity {total_batch_quantity} in the Serial and Batch Bundle does not match with the quantity {item_qty} for the Item {item_code} in the Purchase Receipt # {purchase_receipt}.")
#
#     bundle_doc = frappe.get_doc({
#         "doctype": "Serial and Batch Bundle",
#         "item_code": item_code,
#         "warehouse": warehouse,
#         "type_of_transaction": "Inward",
#         "voucher_type": "Purchase Receipt",
#         "voucher_no": purchase_receipt,
#         "entries": []
#     })
#
#     for detail in batch_details:
#         batch_no = detail.get("batch_no")
#         quantity = detail.get("quantity")
#         if batch_no and quantity:
#             bundle_doc.append("entries", {
#                 "batch_no": batch_no,
#                 "qty": quantity
#             })
#
#     bundle_doc.title = f"{item_code} - {purchase_receipt}"
#     bundle_doc.insert(ignore_permissions=True)
#
#     for item in purchase_receipt_doc.items:
#         if item.item_code == item_code:
#             item.serial_and_batch_bundle = bundle_doc.name
#
#     purchase_receipt_doc.save()
#     frappe.db.commit()
#     return "Serial and Batch Bundle Created Successfully"




#  --------------------------------------


# -------- END Purchase Receipt Doctype that opens a dialog to add batch numbers manually or via CSV  ---------



# ===============================================================


# ===============================================================


# -------- START Check if the "is_return" field is True Update the expense account field for each item  ---------



@frappe.whitelist()
def update_expense_account_on_return_purchase(doc, method):
    if doc.is_return:
        for item in doc.items:
            item.expense_account = frappe.db.get_single_value(
                "payment_entry_test_0002",
                "expense_account_on_return_purchase_a_001"
            )


@frappe.whitelist()
def update_expense_account_on_return_sales(doc, method):
    if doc.is_return:
        for item in doc.items:
            item.income_account = frappe.db.get_single_value(
                "payment_entry_test_0002",
                "income_account_on_return_sales_a_001"
            )



# -------- END Check if the "is_return" field is True Update the expense account field for each item  ---------


# ===============================================================




# ===============================================================


# -------- START Select Sales transactions account on Sales Invoice ---------



@frappe.whitelist()
def select_sales_transactions_account_on_sales_invoice(doc, method=None):
    # ======== START IF Condition Check  =============
    # if doc.data_check_sales_transactions_a_001 == 1:

    data_check_sales_transactions_a_001_check_detail = frappe.get_all(
        "Sales Invoice",
        filters={"name": doc.name},
        fields=["data_check_sales_transactions_a_001", ],
    )
    # data_check_sales_transactions_a_001_check_info = data_check_sales_transactions_a_001_check_detail[0].get('data_check_sales_transactions_a_001')



    if data_check_sales_transactions_a_001_check_detail:
        data_check_sales_transactions_a_001_check_info = data_check_sales_transactions_a_001_check_detail[0].get('data_check_sales_transactions_a_001')

        if data_check_sales_transactions_a_001_check_info == 1:
            # frappe.msgprint(str(data_check_sales_transactions_a_001_check_info))

            # for item in doc.items:
            #     item.expense_account = frappe.db.get_single_value(
            #         "payment_entry_test_0002",
            #         "expense_account_on_return_purchase_a_001"
            #     )

            # "options": "\nمبيعات نقدية\nمبيعات - آجل\nمبيعات التصدير",

            if doc.select_sales_transactions_a_001 == "مبيعات نقدية":
                for item in doc.items:
                    item.income_account = frappe.db.get_single_value(
                        "payment_entry_test_0002",
                        "cash_sales_a_001"
                    )
                frappe.msgprint("مبيعات نقدية", alert=True)
                # create_payment_entry_from_sales_invoice_duplicate_3_cash_only(doc)
                frappe.msgprint("تم إنشاء الدفع النقدى", alert=True)
            elif doc.select_sales_transactions_a_001 == "مبيعات - آجل":
                for item in doc.items:
                    item.income_account = frappe.db.get_single_value(
                        "payment_entry_test_0002",
                        "credit_sales_a_001"
                    )
                frappe.msgprint("مبيعات - آجل", alert=True)
            elif doc.select_sales_transactions_a_001 == "مبيعات التصدير":
                for item in doc.items:
                    item.income_account = frappe.db.get_single_value(
                        "payment_entry_test_0002",
                        "export_sales_a_001"
                    )
                frappe.msgprint("مبيعات التصدير", alert=True)
            else:
                frappe.msgprint("مبيعات", alert=True)



    else:
        frappe.msgprint(f"No Sales Invoice found with name {doc.name}.", alert=True)




# -------- END Select Sales transactions account on Sales Invoice  ---------


# ===============================================================
# ===============================================================















# ===============================================================
# ===============================================================
# ======= START Create payment entry from Sales Invoice Duplicate_2 ==============

@frappe.whitelist()
def create_payment_entry_from_sales_invoice_duplicate_2(doc, method=None):
    """
        create payment entry from sales invoice

        """

    try:
        # if isinstance(doc, str):
        #     sales_invoice = frappe.get_doc("Sales Invoice", doc)

        sales_invoice = doc

        # frappe.msgprint(str(sales_invoice))

        if not sales_invoice.mode_of_payment_a_001:
            pass
        else:
            # Create Payment Entry
            payment_entry = frappe.new_doc("Payment Entry")
            payment_entry.payment_type = "Receive"
            payment_entry.party_type = "Customer"
            payment_entry.party = sales_invoice.customer
            payment_entry.posting_date = nowdate()
            payment_entry.company = sales_invoice.company
            payment_entry.mode_of_payment = sales_invoice.mode_of_payment_a_001
            payment_entry.paid_amount = sales_invoice.outstanding_amount
            payment_entry.received_amount = sales_invoice.outstanding_amount
            payment_entry.reference_no = sales_invoice.name
            payment_entry.reference_date = sales_invoice.posting_date

            if sales_invoice.currency != sales_invoice.company_currency:
                exchange_rate = frappe.get_value('Currency Exchange', {
                    'from_currency': sales_invoice.currency,
                    'to_currency': sales_invoice.company_currency,
                    'transaction_date': sales_invoice.posting_date
                }, 'exchange_rate')

                if not exchange_rate:
                    frappe.throw(
                        f"Exchange rate not found for {sales_invoice.currency} to {sales_invoice.company_currency}.")

                payment_entry.target_exchange_rate = exchange_rate
            else:
                payment_entry.target_exchange_rate = 1

            bank_account = frappe.get_value("Company", doc.company,
                                            "default_receivable_account")

            if not bank_account:
                frappe.throw("Bank Account is not set for the company.")

            if sales_invoice.mode_of_payment_a_001 == "نقداً":
                # mode_of_payment_doc = frappe.get_value("Company", sales_invoice.company, "default_cash_account")

                mode_of_payment_doc = frappe.db.get_single_value(
                    "payment_entry_test_0002",
                    "default_cash_account_payment_a_001"
                )

            else:
                # mode_of_payment_doc = frappe.get_doc('Mode of Payment Account',
                #                                      {'parent': sales_invoice.mode_of_payment_a_001})

                mode_of_payment_doc = frappe.db.get_single_value(
                    "payment_entry_test_0002",
                    "default_visa_account_payment_a_001"
                )

            payment_entry.paid_to = mode_of_payment_doc
            payment_entry.paid_to_account_currency = sales_invoice.company_currency


            # Add the reference to the Sales Invoice
            payment_entry.append("references", {
                "reference_doctype": "Sales Invoice",
                "reference_name": sales_invoice,
                "total_amount": sales_invoice.grand_total,
                "outstanding_amount": sales_invoice.outstanding_amount,
                "allocated_amount": sales_invoice.outstanding_amount
            })

            # Save and Submit the Payment Entry
            payment_entry.insert(ignore_permissions=True)
            payment_entry.submit()

            # Link the Payment Entry
            if "payments" in sales_invoice.meta.get_table_fields():
                sales_invoice.append("payments", {
                    "payment_entry": payment_entry.name,
                    "amount": sales_invoice.outstanding_amount
                })
                sales_invoice.save()

            frappe.msgprint(
                f"Payment Entry {payment_entry.name} has been created and linked to Sales Invoice {sales_invoice}.",
                alert=True
            )

            return payment_entry.name

            sales_invoice.reload()

    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="Payment Entry Creation Error")
        frappe.throw(f"Error creating Payment Entry: {str(e)}")







# ======= END Create payment entry from Sales Invoice Duplicate_2 ==============
#  ==============================================================









# ===============================================================
# ===============================================================
# ======= START Create payment entry from Sales Invoice Duplicate_3 Cash Only ==============


@frappe.whitelist()
def create_payment_entry_from_sales_invoice_duplicate_3_cash_only(doc, method=None):
    """
        create payment entry from sales invoice Duplicate_3 Cash Only

    """
    try:
        # if isinstance(doc, str):
        #     sales_invoice = frappe.get_doc("Sales Invoice", doc)

        sales_invoice = doc

        # frappe.msgprint(str(sales_invoice))

        # # ========================
        # if isinstance(doc, str):
        #     sales_invoice = frappe.get_doc("Sales Invoice", doc)
        # else:
        #     sales_invoice = doc
        # # ========================

        # # Fetch Data "branch_link_mode_of_payment_a_002" from Sales Inoice
        # fetch_detail_branch_link_mode_of_payment_a_002 = frappe.get_all(
        #     "Sales Invoice",
        #     filters={"name": doc.name},
        #     fields=["branch_link_mode_of_payment_a_002", ],
        # )
        # fetch_detail_branch_link_mode_of_payment_a_002_info = fetch_detail_branch_link_mode_of_payment_a_002[0].get('branch_link_mode_of_payment_a_002')
        #
        # # frappe.msgprint(str(fetch_detail_branch_link_mode_of_payment_a_002_info))

        if doc.select_sales_transactions_a_001 == "مبيعات نقدية":

            # Fetch "branch_link_mode_of_payment_a_002" from the Sales Invoice
            fetch_detail_branch_link_mode_of_payment_a_002 = frappe.get_value(
                "Sales Invoice",
                sales_invoice.name,
                "branch_link_mode_of_payment_a_002"
            )

            if not fetch_detail_branch_link_mode_of_payment_a_002:
                frappe.msgprint(
                    "Branch link mode of payment not found in Sales Invoice.",
                    alert=True
                )
                return

            # # Fetch the matching Mode of Payment record
            mode_of_payment_data = frappe.get_all(
                "Mode of Payment",
                filters={"branch_link_mode_of_payment_a_001": fetch_detail_branch_link_mode_of_payment_a_002},
                fields=["name", "type", "branch_link_mode_of_payment_a_001"]
            )

            if mode_of_payment_data:
                mode_of_payment_name = mode_of_payment_data[0].get('name')

            # Each row in the child table is accessible as an object with its fields
            mode_of_payment_data_b = frappe.get_doc("Mode of Payment", mode_of_payment_name)

            # Access the child table 'accounts'
            if mode_of_payment_data_b.accounts:
                for account in mode_of_payment_data_b.accounts:
                    default_account = account.default_account
                    # frappe.msgprint(f"Account: {default_account}")
            else:
                frappe.msgprint("No accounts linked to this Mode of Payment.")

            # frappe.msgprint(str(fetch_detail_branch_link_mode_of_payment_a_002))
            # frappe.msgprint(str(mode_of_payment_data))
            # # frappe.msgprint(str(mode_of_payment_data_b))
            # frappe.msgprint(str(mode_of_payment_name))




            if not sales_invoice.data_check_sales_transactions_a_001:
                pass
            else:
                # frappe.msgprint(str(mode_of_payment_name))
                # frappe.msgprint(str(default_account))
                # # frappe.msgprint(str(mode_of_payment_name))
                # # # Create Payment Entry
                payment_entry = frappe.new_doc("Payment Entry")
                payment_entry.payment_type = "Receive"
                payment_entry.party_type = "Customer"
                payment_entry.party = sales_invoice.customer
                payment_entry.posting_date = nowdate()
                payment_entry.company = sales_invoice.company
                # payment_entry.mode_of_payment = sales_invoice.mode_of_payment_a_001
                # Assign mode_of_payment
                if mode_of_payment_name:
                    payment_entry.mode_of_payment = str(mode_of_payment_name)
                else:
                    frappe.throw("No matching Mode of Payment found. Cannot create Payment Entry.")
                payment_entry.paid_amount = sales_invoice.outstanding_amount
                payment_entry.received_amount = sales_invoice.outstanding_amount
                payment_entry.reference_no = sales_invoice.name
                payment_entry.reference_date = sales_invoice.posting_date

                if sales_invoice.currency != sales_invoice.company_currency:
                    exchange_rate = frappe.get_value('Currency Exchange', {
                        'from_currency': sales_invoice.currency,
                        'to_currency': sales_invoice.company_currency,
                        'transaction_date': sales_invoice.posting_date
                    }, 'exchange_rate')

                    if not exchange_rate:
                        frappe.throw(
                            f"Exchange rate not found for {sales_invoice.currency} to {sales_invoice.company_currency}.")

                    payment_entry.target_exchange_rate = exchange_rate
                else:
                    payment_entry.target_exchange_rate = 1

                bank_account = frappe.get_value("Company", doc.company,
                                                "default_receivable_account")

                if not bank_account:
                    frappe.throw("Bank Account is not set for the company.")

                payment_entry.paid_to = default_account
                payment_entry.paid_to_account_currency = sales_invoice.company_currency


                # Add the reference to the Sales Invoice
                payment_entry.append("references", {
                    "reference_doctype": "Sales Invoice",
                    "reference_name": sales_invoice,
                    "total_amount": sales_invoice.grand_total,
                    "outstanding_amount": sales_invoice.outstanding_amount,
                    "allocated_amount": sales_invoice.outstanding_amount
                })

                # Save and Submit the Payment Entry
                payment_entry.insert(ignore_permissions=True)
                payment_entry.submit()

                # Link the Payment Entry
                if "payments" in sales_invoice.meta.get_table_fields():
                    sales_invoice.append("payments", {
                        "payment_entry": payment_entry.name,
                        "amount": sales_invoice.outstanding_amount
                    })
                    sales_invoice.save()

                frappe.msgprint(
                    f"Payment Entry {payment_entry.name} has been created and linked to Sales Invoice {sales_invoice}.",
                    alert=True
                )

                return payment_entry.name

                sales_invoice.reload()

    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="Error in fetch_branch_and_mode_of_payment")
        frappe.throw(f"Error creating Payment Entry: {str(e)}")





# ======= END Create payment entry from Sales Invoice Duplicate_3 Cash Only  ==============
#  ==============================================================











# ===============================================================
# ===============================================================


# -------- START Check if Select Account Purchase Invoice for table Items  ---------




@frappe.whitelist()
def select_account_purchase_invoice_for_table_items(doc, method=None):
    # ======== START IF Condition Check  =============
    # if doc.data_check_purchase_transactions_a_001 == 1:

    # Fetch 'data_check_purchase_transactions_a_001'
    data_check_purchase_transactions_a_001_check_detail = frappe.get_all(
        "Purchase Invoice",
        filters={"name": doc.name},
        fields=["data_check_purchase_transactions_a_001"],
    )

    if data_check_purchase_transactions_a_001_check_detail:
        data_check_purchase_transactions_a_001_check_info = data_check_purchase_transactions_a_001_check_detail[0].get(
            'data_check_purchase_transactions_a_001')

        if data_check_purchase_transactions_a_001_check_info == 1:
            for item in doc.items:
                item.expense_account = doc.select_account_purchase_invoice_for_table_items_a_001
                frappe.msgprint(
                    f"Expense Account {doc.select_account_purchase_invoice_for_table_items_a_001} has been assigned to table items",
                    alert=True
                )
    else:
        frappe.msgprint(f"No Purchase Invoice found with name {doc.name}.", alert=True)


# -------- END Check if Select Account Purchase Invoice for table Items  ---------


# ===============================================================
# ===============================================================











# ===============================================================
# ===============================================================


# -------- START Fetch the selectable options based on the value of data_check_purchase_transactions_a_001 in the Purchase Invoice ---------


@frappe.whitelist()
def get_all_child_table_values(doc, method=None):
    try:
        child_table_entries = frappe.get_all(
            "payment_entry_test_0003",
            fields=["select_a_account_purchase_invoice_for_child_table_items_a_001"]
        )

        data_values = [entry["select_a_account_purchase_invoice_for_child_table_items_a_001"] for entry in
                       child_table_entries if entry["select_a_account_purchase_invoice_for_child_table_items_a_001"]]

        # frappe.msgprint(f"Retrieved Values: {data_values}")

        return data_values
    except Exception as e:
        frappe.throw(f"Unexpected Error: {str(e)}")



# -------- END Fetch the selectable options based on the value of data_check_purchase_transactions_a_001 in the Purchase Invoice ---------


# ===============================================================
# ===============================================================









# ===============================================================
# ===============================================================


# -------- START AA Check if Select Account Purchase Invoice for table Items  ---------


@frappe.whitelist()
def select_account_purchase_invoice_for_table_items_aa(doc, method=None):
    # ======== START IF Condition Check  =============
    # if doc.data_check_purchase_transactions_a_001 == 1:

    # Fetch 'data_check_purchase_transactions_a_001'
    data_check_purchase_transactions_a_001_check_detail = frappe.get_all(
        "Purchase Invoice",
        filters={"name": doc.name},
        fields=["data_check_purchase_transactions_a_001"],
    )

    if data_check_purchase_transactions_a_001_check_detail:
        data_check_purchase_transactions_a_001_check_info = data_check_purchase_transactions_a_001_check_detail[0].get(
            'data_check_purchase_transactions_a_001')

        if data_check_purchase_transactions_a_001_check_info == 1:
            for item in doc.items:
                item.expense_account = doc.select_account_purchase_invoice_for_table_items_aa_001
                frappe.msgprint(
                    f"Expense Account {doc.select_account_purchase_invoice_for_table_items_aa_001} has been assigned to table items",
                    alert=True
                )
    else:
        frappe.msgprint(f"No Purchase Invoice found with name {doc.name}.", alert=True)


# -------- END AA Check if Select Account Purchase Invoice for table Items  ---------


# ===============================================================
# ===============================================================











# ===============================================================
# ===============================================================


# -------- START Check if Select Data Check Sales Return transactions  ---------




@frappe.whitelist()
def select_income_account_on_return_sales_for_table_items(doc, method=None):
    # ======== START IF Condition Check  =============
    # if doc.data_check_sales_transactions_a_001_aa == 1:

    # Fetch 'data_check_purchase_transactions_a_001'
    data_check_sales_transactions_a_001_aa_check_detail = frappe.get_all(
        "Sales Invoice",
        filters={"name": doc.name},
        fields=["data_check_sales_transactions_a_001_aa"],
    )

    if data_check_sales_transactions_a_001_aa_check_detail:
        data_check_sales_transactions_a_001_aa_check_info = data_check_sales_transactions_a_001_aa_check_detail[0].get(
            'data_check_sales_transactions_a_001_aa')

        if data_check_sales_transactions_a_001_aa_check_info == 1:
            for item in doc.items:
                item.income_account = doc.income_account_on_return_sales_a_001_aa
                frappe.msgprint(
                    f"Income Account {doc.income_account_on_return_sales_a_001_aa} has been assigned to table items",
                    alert=True
                )
    else:
        frappe.msgprint(f"No Sales Return found with name {doc.name}.", alert=True)


# -------- END Check if Select Data Check Sales Return transactions  ---------


# ===============================================================
# ===============================================================







# ===============================================================
# ===============================================================


# -------- START Check if Select Data Check Purchase Return transactions  ---------




@frappe.whitelist()
def select_expense_account_on_return_purchase_for_table_items(doc, method=None):
    # ======== START IF Condition Check  =============
    # if doc.data_check_purchase_transactions_a_001_aa == 1:

    # Fetch 'data_check_purchase_transactions_a_001_aa'
    data_check_purchase_transactions_a_001_aa_check_detail = frappe.get_all(
        "Purchase Invoice",
        filters={"name": doc.name},
        fields=["data_check_purchase_transactions_a_001_aa"],
    )

    if data_check_purchase_transactions_a_001_aa_check_detail:
        data_check_purchase_transactions_a_001_aa_check_info = data_check_purchase_transactions_a_001_aa_check_detail[0].get(
            'data_check_purchase_transactions_a_001_aa')

        if data_check_purchase_transactions_a_001_aa_check_info == 1:
            for item in doc.items:
                item.expense_account = doc.expense_account_on_return_purchase_a_001_aa
                frappe.msgprint(
                    f"Expense Account {doc.expense_account_on_return_purchase_a_001_aa} has been assigned to table items",
                    alert=True
                )
    else:
        frappe.msgprint(f"No Purchase Return found with name {doc.name}.", alert=True)


# -------- END Check if Select Data Check Purchase Return transactions  ---------


# ===============================================================
# ===============================================================









# ===============================================================
# ===============================================================


# -------- START Fetch stock details (warehouse, quantity available, reserved quantity) for the given item code.  ---------
# -------- START Fetch the last 3 invoices (invoice number, posting date, rate) for the given item code.  -----------------


@frappe.whitelist()
def get_item_stock_details(item_code):
    """
    Fetch stock details (warehouse, quantity available, reserved quantity) for the given item code.
    """
    stock_details = frappe.db.sql("""
        SELECT warehouse, actual_qty, reserved_qty
        FROM `tabBin`
        WHERE item_code = %s
    """, item_code, as_dict=True)
    return {"stock_details": stock_details}


@frappe.whitelist()
def get_last_invoices(item_code):
    """
    Fetch the last 3 invoices (invoice number, posting date, rate) for the given item code.
    """
    last_invoices = frappe.db.sql("""
        SELECT `tabSales Invoice`.name as invoice_no, `tabSales Invoice`.posting_date, `tabSales Invoice Item`.rate
        FROM `tabSales Invoice`
        INNER JOIN `tabSales Invoice Item` ON `tabSales Invoice Item`.parent = `tabSales Invoice`.name
        WHERE `tabSales Invoice Item`.item_code = %s
        ORDER BY `tabSales Invoice`.posting_date DESC
        LIMIT 3
    """, item_code, as_dict=True)
    return {"last_invoices": last_invoices}



# -------- END Fetch stock details (warehouse, quantity available, reserved quantity) for the given item code.  ---------
# -------- END Fetch the last 3 invoices (invoice number, posting date, rate) for the given item code.  -----------------


# ===============================================================
# ===============================================================







# ===============================================================
# ===============================================================
# ===============================================================






















# ===============================================================
# ===============================================================
# ===============================================================
# ===============================================================


