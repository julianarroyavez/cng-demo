from app.domain.payment_schema import Invoices
from app.log import LOG


class InvoicesRepository:

    def __init__(self):
        pass  # empty is required

    def insert(self, invoice_number, user_id, order_id, payment_id, comment):
        return Invoices.create(
            invoice_number=invoice_number,
            created_by=user_id,
            modified_by=user_id,
            comment=comment,
            order_id=order_id,
            payment_id=payment_id
        )
