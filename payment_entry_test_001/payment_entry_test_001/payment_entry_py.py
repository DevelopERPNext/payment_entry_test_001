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



