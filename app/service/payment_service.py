import datetime
import uuid

from app.domain.payment_schema import PaymentState, OrderTypes
from app.log import PAYTM_LOG
from app.repository.mobile_devices_repository import MobileDevicesRepository
from app.repository.payments_repository import PaymentsRepository
from app.util.datetime_util import datetime_now


class PaymentService:

    def generate_payment_for_encashment(self, device_token, user_id, order, sender_id, receiver_id):
        PAYTM_LOG.info('inside payment method')
        payment_repository = PaymentsRepository()
        mobile_devices_repository = MobileDevicesRepository()

        device = mobile_devices_repository.fetch_by_device_token(device_token=device_token, now=datetime_now())

        payment_id = str(uuid.uuid4())
        PAYTM_LOG.info('inside payment method 2')
        payment = payment_repository.insert(payment_id=payment_id, user_id=user_id, order_id=order.order_id,
                                            sender_id=sender_id, receiver_id=receiver_id,
                                            total_amount=order.total, today=datetime.date.today(),
                                            payment_status=PaymentState.ProcessRequired, device_id=device.record_id,
                                            gateway_name=None)
        return payment

    def generate_payment(self, device_token, user_id, order, sender_id, receiver_id):
        PAYTM_LOG.info('inside payment method')
        payment_repository = PaymentsRepository()
        mobile_devices_repository = MobileDevicesRepository()

        device = mobile_devices_repository.fetch_by_device_token(device_token=device_token, now=datetime_now())

        payment_id = str(uuid.uuid4())

        payment = payment_repository.insert(payment_id=payment_id, user_id=user_id, order_id=order.order_id,
                                            sender_id=sender_id, receiver_id=receiver_id,
                                            total_amount=order.total, today=datetime.date.today(),
                                            payment_status=PaymentState.Init, device_id=device.record_id,
                                            gateway_name='paytm')
        return payment

    def generate_payment_tokens(self, payment, order):
        payment_repository = PaymentsRepository()
        payment_id = str(uuid.uuid4())

        payment = payment_repository.insert(payment_id=payment_id, user_id=payment.created_by, order_id=order.order_id,
                                            sender_id=payment.receiver_id, receiver_id=payment.sender_id,
                                            total_amount=order.total, today=datetime.date.today(),
                                            payment_status=PaymentState.Success, device_id=payment.device_id,
                                            gateway_name=None)
        return payment

    def init_success_update_database(self, payment):
        payment.payment_status = PaymentState.ProcessRequired
        PaymentsRepository().update(payment)

    def get_transaction_history(self, account_id, offset, limit, transaction_types):

        payment_repository = PaymentsRepository()
        transactions = []

        for payment in payment_repository.fetch_payments(account_id=account_id, offset=offset, limit=limit, transaction_types=transaction_types):
            PAYTM_LOG.info(payment.id)
            transaction = {
                'txnId': payment.id,
                'orderId': payment.order.order_id,
                'status': payment.payment_status.value,
                'date': payment.modified_on,
                'remark': payment.comment,
                'transactionType': '',
                'message': '',
                'orderAmount': {
                    'value': payment.order_amount
                },
                'sender': {
                    'id': payment.sender_account.record_id,
                    'name': payment.sender_account.alias_name,
                    'wallet': {
                        'id': payment.sender_account.sender_wallet.record_id,
                        'name': payment.sender_account.sender_wallet.name
                    }
                },
                'receiver': {
                    'id': payment.receiver_account.record_id,
                    'name': payment.receiver_account.alias_name,
                    'wallet': {
                        'id': payment.receiver_account.receiver_wallet.record_id,
                        'name': payment.receiver_account.receiver_wallet.name
                    }
                },
                'order': {
                    'orderId': payment.order.order_id,
                    'orderType': payment.order.order_type.value,
                    'orderStatus': payment.order.order_status,
                    'totalAmount': {
                        'value': payment.order.total,
                        'currency': 'TOKEN'
                    }
                }

            }

            try:
                transaction['_links']['invoice'] = {
                        'href': '/api/v1/invoices/' + str(payment.invoices.id)
                    }
            except Exception:
                pass

            try:
                transaction['sender']['user'] = {
                        'id': payment.sender_account.sender_user.record_id,
                        'customerId': payment.sender_account.sender_user.customer_id,
                        'phoneNumber': payment.sender_account.sender_user.phone_number,
                        'verified': payment.sender_account.sender_user.verified
                    }
            except Exception:
                pass

            try:
                transaction['sender']['station'] = {
                        'id': payment.sender_account.sender_station.record_id,
                        'stationCode': payment.sender_account.sender_station.record_id,
                        'verified': payment.sender_account.sender_station.verified
                    }
            except Exception:
                pass

            try:
                transaction['receiver']['user'] = {
                    'id': payment.receiver_account.receiver_user.record_id,
                    'customerId': payment.receiver_account.receiver_user.customer_id,
                    'phoneNumber': payment.receiver_account.receiver_user.phone_number,
                    'verified': payment.receiver_account.receiver_user.verified
                }
            except Exception:
                pass

            try:
                transaction['receiver']['station'] = {
                    'id': payment.receiver_account.receiver_station.record_id,
                    'stationCode': payment.receiver_account.receiver_station.record_id,
                    'verified': payment.receiver_account.receiver_station.verified
                }
            except Exception:
                pass

            transaction = self.append_token_credit_debit_order_type_for_transaction_history(transaction=transaction)
            transaction = self.append_token_transfer_order_type_for_transaction_history(transaction=transaction,
                                                                                        account_id=account_id)

            transactions.append(transaction)

        response = {
            'offset': offset,
            'limit': limit,
            'transactions': transactions,
            "_links": {
                "next": {
                    "href": "/api/v1/wallets/self/transactions?offset=10"
                },
                "last": {
                    "href": "/api/v1/wallets/self/transactions?offset=?"
                },
                "previous": {
                    "href": "/api/v1/wallets/self/transactions?offset=0"
                },
                "first": {
                    "href": "/api/v1/wallets/self/transactions?offset=0"
                }
            }
        }

        return response

    def append_token_credit_debit_order_type_for_transaction_history(self, transaction):

        if transaction['order']['orderType'] == OrderTypes.PurchaseToken.value:
            transaction['transactionType'] = 'CREDIT'
            transaction['message'] = 'Tokens Purchased'

        if transaction['order']['orderType'] == OrderTypes.CancelBooking.value:
            transaction['transactionType'] = 'CREDIT'
            transaction['message'] = 'Tokens Refunded'

        if transaction['order']['orderType'] == OrderTypes.EncashToken.value:
            transaction['transactionType'] = 'DEBIT'
            transaction['message'] = 'Tokens Encashed'

        if transaction['order']['orderType'] == OrderTypes.PayForBooking.value:
            transaction['transactionType'] = 'DEBIT'
            transaction['message'] = 'Tokens Sold'

        if transaction['order']['orderType'] == OrderTypes.PayForToken.value:
            transaction['transactionType'] = 'CREDIT_FAILURE'
            transaction['message'] = 'Failure in Purchasing Tokens'

        return transaction

    def append_token_transfer_order_type_for_transaction_history(self, transaction, account_id):

        if transaction['order']['orderType'] == OrderTypes.TransferToken.value and str(
                transaction['sender'].get('user', transaction['sender'].get('station', {})).get('id',
                                                                                                '')) == account_id:
            transaction['transactionType'] = 'DEBIT'
            transaction['message'] = 'Tokens Transferred'

        if transaction['order']['orderType'] == OrderTypes.TransferToken.value and str(
                transaction['receiver'].get('user', transaction['receiver'].get('station', {})).get('id',
                                                                                                    '')) == account_id:
            transaction['transactionType'] = 'CREDIT'
            transaction['message'] = 'Tokens Transferred'

        return transaction



