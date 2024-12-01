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
                mode_of_payment_doc = frappe.get_value("Company", sales_invoice.company, "default_cash_account")
            else:
                mode_of_payment_doc = frappe.get_doc('Mode of Payment Account',
                                                     {'parent': sales_invoice.mode_of_payment_a_001})


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




# --------  Purchase Receipt Doctype that opens a dialog to add batch numbers manually or via CSV  ---------







@frappe.whitelist()
def save_batch_details(batch_details, item_code, warehouse, purchase_receipt):
    import json

    batch_details = json.loads(batch_details)
    purchase_receipt_doc = frappe.get_doc("Purchase Receipt", purchase_receipt)

    item_qty = next((item.qty for item in purchase_receipt_doc.items if item.item_code == item_code), None)
    if item_qty is None:
        frappe.throw(f"Item {item_code} not found in the Purchase Receipt.")

    total_batch_qty = sum(detail.get("quantity", 0) for detail in batch_details)
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

    # bundle_doc = frappe.get_doc({
    #     "doctype": "Serial and Batch Bundle",
    #     "item_code": item_code,
    #     "warehouse": warehouse,
    #     "type_of_transaction": "Inward",
    #     "voucher_type": "Purchase Receipt",
    #     "voucher_no": purchase_receipt,
    #     "entries": []
    # })
    #
    # for detail in batch_details:
    #     batch_no = detail.get("batch_no")
    #     quantity = detail.get("quantity")
    #     if batch_no and quantity:
    #         bundle_doc.append("entries", {
    #             "batch_no": batch_no,
    #             "quantity": quantity
    #         })
    #
    # bundle_doc.title = f"{item_code} - {purchase_receipt}"
    #
    # bundle_total_qty = sum([entry.get("quantity", 0) for entry in bundle_doc.entries])
    # if bundle_total_qty != item_qty:
    #     frappe.throw(f"Total quantity in the bundle ({bundle_total_qty}) does not match the item quantity ({item_qty}) in the Purchase Receipt.")
    #
    # bundle_doc.insert(ignore_permissions=True)
    #
    # for item in purchase_receipt_doc.items:
    #     if item.item_code == item_code:
    #         item.serial_and_batch_bundle = bundle_doc.name

    purchase_receipt_doc.save()
    frappe.db.commit()
    return "Success"




#  --------------------------------------





#
#
# @frappe.whitelist()
# def add_batch_to_doctype(batch_details, item_code, warehouse):
#     import json
#
#     batch_details = json.loads(batch_details)
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
#     return "Batch added successfully."
#
#
# @frappe.whitelist()
# def add_to_serial_and_batch_bundle(batch_details, item_code, warehouse, purchase_receipt):
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
#     if total_batch_qty != item_qty:
#         frappe.throw(f"Total batch quantity ({total_batch_qty}) does not match item quantity ({item_qty}) for item {item_code} in Purchase Receipt {purchase_receipt}.")
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
#                 "quantity": quantity
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
#     return "Serial and Batch Bundle added successfully."
#











#  --------------------------------------

# @frappe.whitelist()
# def save_batch_details(batch_details, item_code, warehouse, purchase_receipt):
#     import json
#     batch_details = json.loads(batch_details)
#
#     for detail in batch_details:
#         batch_no = detail.get("batch_no")
#         quantity = detail.get("quantity")
#
#         if batch_no and quantity:
#             batch = frappe.get_doc({
#                 "doctype": "Batch",
#                 "batch_id": batch_no,
#                 "item": item_code,
#                 "warehouse": warehouse
#             })
#             if not batch.get("batch_qty"):
#                 batch.batch_qty = 0
#             batch.batch_qty += float(quantity)
#             batch.save()
#
#             doc = frappe.get_doc({
#                 "doctype": "Serial and Batch Bundle",
#                 "item_code": item_code,
#                 "batch_no": batch_no,
#                 "warehouse": warehouse,
#                 "quantity": quantity,
#                 "type_of_transaction": "Inward",
#                 "voucher_type": "Purchase Receipt",
#                 "voucher_no": purchase_receipt,
#                 "entries": [
#                     {
#                         "batch_no": batch_no,
#                         "quantity": quantity
#                     }
#                 ]
#             })
#
#             if hasattr(doc, "title"):
#                 doc.title = f"{item_code} - {batch_no}"
#
#             doc.insert(ignore_permissions=True)
#
#     return "Success"

#  --------------------------------------




# ===============================================================




