from app.repository.invoices_repository import InvoicesRepository
import uuid

class InvoiceService:

    def insert(self, user_id, order_id, payment, comment):
        invoice_repository = InvoicesRepository()
        invoice_number = uuid.uuid4()
        return invoice_repository.insert(invoice_number=invoice_number, user_id=user_id, order_id=order_id, payment_id=payment, comment=comment)


