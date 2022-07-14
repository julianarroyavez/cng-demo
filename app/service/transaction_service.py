from decimal import Decimal

from app.database import db_session
from app.domain.auth_schema import UserRoles
from app.domain.payment_schema import PaymentState, OrderTypes
from app.repository.mobile_devices_repository import MobileDevicesRepository
from app.repository.payments_repository import PaymentsRepository
from app.repository.station_assignment_repository import StationAssignmentRepository
from app.repository.user_group_rel_repository import UserGroupRelRepository
from app.repository.wallets_repository import WalletsRepository
from app.repository.order_items_repository import OrderItemsRepository
from app.repository.orders_repository import OrdersRepository
from app.repository.users_repository import UsersRepository
from app.service.invoice_service import InvoiceService
from app.service.notification_service import NotificationService
from app.service.order_service import OrderService
from app.service.payment_service import PaymentService
from app.service.paytm_service import PaytmService
import app.service.paytm_service as paytm_constant
from app.log import LOG
from app.util.datetime_util import datetime_now
from app.errors import InvalidParameterError, InvalidFieldError, FieldErrors, ConflictParameterError, ErrorMessages, \
    MissingFieldError
from app.util.notification_factory import NotificationFactory

test_comment = 'Test Comment'


class TransactionService:

    def transfer_tokens(self, sender_wallet, receiver_wallet, count_of_tokens):

        wallets_repository = WalletsRepository()
        wallets_repository.update_balance(record=sender_wallet, new_balance=sender_wallet.balance - count_of_tokens)
        LOG.info('hygge mart balance updated')

        wallets_repository.update_balance(record=receiver_wallet, new_balance=receiver_wallet.balance + count_of_tokens)
        LOG.info('User balance updated')

    def transit_tokens(self, sender_wallet, count_of_tokens):
        LOG.info(type(count_of_tokens))
        wallets_repository = WalletsRepository()
        wallets_repository.update_transit_balance(record=sender_wallet,
                                                  new_balance=Decimal(sender_wallet.balance) - Decimal(count_of_tokens),
                                                  new_transit_balance=Decimal(sender_wallet.in_transit or 0) + Decimal(
                                                      count_of_tokens))
        LOG.info('User transit balance updated')

    def init_success_update_database(self, payment):
        payment.payment_status = PaymentState.ProcessRequired
        PaymentsRepository().update(payment)

    def purchase_tokens_from_hygge_mart(self, receiver_user_id, receiver_account_id, order, payment, no_of_tokens):
        with db_session.atomic():
            wallet_repository = WalletsRepository()
            receiver_wallet = wallet_repository.fetch_by_account_id(account_id=receiver_account_id, now=datetime_now())
            hygge_mart_wallet = wallet_repository.fetch_hygge_mart_wallet()
            self.transfer_tokens(hygge_mart_wallet, receiver_wallet, no_of_tokens)

            order_service = OrderService()
            newly_created_order = order_service.generate_purchase_order_tokens(order)

            payment_service = PaymentService()
            payment = payment_service.generate_payment_tokens(payment, newly_created_order)

            invoice_service = InvoiceService()
            invoice_service.insert(user_id=receiver_user_id, order_id=order, payment=payment, comment=test_comment)

            LOG.info('purchase done')

    def txn_success_update_database(self, req, response):

        payment_repository = PaymentsRepository()
        order_items_repository = OrderItemsRepository()

        order_id = response['body']['orderId']

        # todo: it should not fetch using order id, we should use txn_id
        new_payment = payment_repository.fetch_by_order_id(order_id=order_id)

        new_payment.payment_status = PaymentState.Success
        new_payment.gateway_response = response
        new_payment.client_response = req.context['data']['options']

        payment_repository.update(new_payment)
        LOG.info('Payment table updated')

        # todo: order item to order mapping is one to many,items could be many but for purchase s of now it is only one
        purchased_tokens = order_items_repository.fetch_by_order_id(order_id=order_id).quantity
        LOG.info('purchased_tokens %s' % purchased_tokens)

        orders_repository = OrdersRepository()
        new_order = orders_repository.fetch_by_order_id(order_id=order_id)

        if UserRoles.StationOwner.value in req.context['auth_claims']['role']:
            receiver = StationAssignmentRepository().fetch_by_user_record_id(now=datetime_now(),
                                                                             user_id=req.context['auth_claims']['user'])
            receiver_id = receiver.station_record_id
        else:
            receiver_id = req.context['auth_claims']['user']

        transaction_service = TransactionService()
        transaction_service.purchase_tokens_from_hygge_mart(receiver_user_id=req.context["auth_claims"].get('user'),
                                                            receiver_account_id=receiver_id,
                                                            order=new_order,
                                                            payment=new_payment,
                                                            no_of_tokens=purchased_tokens)

    def txn_failure_update_database(self, req, response):
        payment_repository = PaymentsRepository()
        order_id = response['body']['orderId']

        new_payment = payment_repository.fetch_by_order_id(order_id=order_id)

        new_payment.payment_status = PaymentState.VerificationFailed
        new_payment.gateway_response = response
        new_payment.client_response = req.context['data']['options']

        payment_repository.update(new_payment)

        orders_repository = OrdersRepository()
        order = orders_repository.fetch_by_order_id(order_id)
        order.order_status = 'FAILURE'
        orders_repository.update(order)
        LOG.info('Payment table updated')

    def txn_cancelled_update_database(self, req, response, order_id):
        payment_repository = PaymentsRepository()

        new_payment = payment_repository.fetch_by_order_id(order_id=order_id)

        new_payment.payment_status = PaymentState.TxnCancelled
        new_payment.gateway_response = response
        new_payment.client_response = req.context['data']['options']

        payment_repository.update(new_payment)

        orders_repository = OrdersRepository()
        order = orders_repository.fetch_by_order_id(order_id)
        order.order_status = 'CANCELLED'
        orders_repository.update(order)
        LOG.info('Txn cancelled Payment table updated')

    def final_payment_update(self, payment_status_response, req, user_id=None, device_token=None):
        order_id = payment_status_response['body']['orderId']
        notification_factory = NotificationFactory()
        payment_repository = PaymentsRepository()
        notification_service = NotificationService()

        payments = payment_repository.fetch_by_order_id(order_id=order_id)

        if payment_status_response['body']['resultInfo']['resultStatus'] == 'TXN_SUCCESS':
            self.txn_success_update_database(req=req, response=payment_status_response)
            notification = notification_factory.create_and_queue_notification(data=payments, user_id=user_id,
                                                                              device=None,
                                                                              device_token=device_token,
                                                                              trigger='Token_add')

        if payment_status_response['body']['resultInfo']['resultStatus'] == 'TXN_FAILURE':
            self.txn_failure_update_database(req=req, response=payment_status_response)
            notification = notification_factory.create_and_queue_notification(data=payments, user_id=user_id,
                                                                              device=None,
                                                                              device_token=device_token,
                                                                              trigger='Token_failed')

        if (len(req.context['data']['gateway']['sdkFailure']) != 0) and \
                (payment_status_response['body']['resultInfo']['resultStatus'] == 'PENDING'):
            paytm_service = PaytmService()
            txn_cancel_response = paytm_service.cancel_txn(order_id=order_id)

            self.txn_cancelled_update_database(req=req, response=txn_cancel_response, order_id=order_id)
            notification = notification_factory.create_and_queue_notification(data=payments, user_id=user_id,
                                                                              device=None,
                                                                              device_token=device_token,
                                                                              trigger='Token_failed')

            notification_service.insert_notification(notifications=notification['notifications'],
                                                     to_device=notification['to_device'])

            return {
                "txnId": payment_status_response['body']['txnId'],
                "orderId": payment_status_response['body']['orderId'],
                "status": 'TXN_CANCELLED',
                "statusDesc": 'PaytmService has been cancelled',
                "orderAmount": {
                    "value": payment_status_response['body']['txnAmount'],
                    "currency": "INR"
                },
                "gateway": {
                    "mId": paytm_constant.MERCHANT_ID
                }
            }

        notification_service.insert_notification(notifications=notification['notifications'],
                                                 to_device=notification['to_device'])

        return {
            "txnId": payment_status_response['body']['txnId'],
            "orderId": payment_status_response['body']['orderId'],
            "status": payment_status_response['body']['resultInfo']['resultStatus'],
            "statusDesc": payment_status_response['body']['resultInfo']['resultMsg'],
            "orderAmount": {
                "value": payment_status_response['body']['txnAmount'],
                "currency": "INR"
            },
            "gateway": {
                "mId": paytm_constant.MERCHANT_ID
            }
        }

    def verify_purchase(self, req, txn_id, user_id, device_token):
        paytm_service = PaytmService()
        payment_status_response = paytm_service.verify_txn(unique_order_id=req.context['data']['orderId'])

        response = self.final_payment_update(payment_status_response=payment_status_response, req=req,
                                             user_id=user_id, device_token=device_token)
        LOG.info('verify purchase response: %s' % response)

        response['txnId'] = txn_id
        return response

    def pay_for_booking(self, device_token, user, amount, service_rate_table_id=None, days_of_week=None,
                        segments_of_day=None, service_master_id=None, rated_power_id=None):
        with db_session.atomic():
            wallet_repository = WalletsRepository()
            sender_wallet = wallet_repository.fetch_by_account_id(account_id=user.record_id, now=datetime_now())
            hygge_booking_wallet = wallet_repository.fetch_hygge_booking_bucket_wallet()
            self.transfer_tokens(sender_wallet, hygge_booking_wallet, Decimal(amount))

            order_service = OrderService()
            order = order_service.generate_purchase_order(user_id=user.record_id, amount=amount, from_unit='TOKEN',
                                                          to_unit='TOKEN', order_type=OrderTypes.PayForBooking,
                                                          penalty_amount=None,
                                                          service_rate_table_id=service_rate_table_id,
                                                          days_of_week=days_of_week, segments_of_day=segments_of_day,
                                                          service_master_id=service_master_id,
                                                          rated_power_id=rated_power_id)

            payment_service = PaymentService()
            payment = payment_service.generate_payment(device_token=device_token,
                                                       user_id=user.record_id,
                                                       order=order,
                                                       sender_id=user.record_id,
                                                       receiver_id=hygge_booking_wallet)

            invoice_service = InvoiceService()
            LOG.info('Payment done')
            return invoice_service.insert(user_id=user.record_id, order_id=order, payment=payment,
                                          comment=test_comment)

    def cancel_booking(self, user_id, device_token, amount, penalty_amount):
        with db_session.atomic():
            wallet_repository = WalletsRepository()
            sender_wallet = wallet_repository.fetch_by_account_id(account_id=user_id, now=datetime_now())
            hygge_booking_wallet = wallet_repository.fetch_hygge_booking_bucket_wallet()
            self.transfer_tokens(hygge_booking_wallet, sender_wallet, Decimal(amount - penalty_amount))

            order_service = OrderService()
            order = order_service.generate_purchase_order(user_id=user_id, amount=amount, from_unit='TOKEN',
                                                          to_unit='TOKEN', order_type=OrderTypes.CancelBooking,
                                                          penalty_amount=penalty_amount)

            payment_service = PaymentService()
            payment = payment_service.generate_payment(device_token=device_token,
                                                       user_id=user_id,
                                                       order=order,
                                                       sender_id=user_id,
                                                       receiver_id=hygge_booking_wallet)

            invoice_service = InvoiceService()
            invoice_service.insert(user_id=user_id, order_id=order, payment=payment, comment=test_comment)

            hygge_mart_wallet = wallet_repository.fetch_hygge_mart_wallet()
            self.transfer_tokens(hygge_booking_wallet, hygge_mart_wallet, Decimal(penalty_amount))

            order = order_service.generate_purchase_order(user_id=user_id, amount=penalty_amount, from_unit='TOKEN',
                                                          to_unit='TOKEN', order_type=OrderTypes.CancelBooking,
                                                          penalty_amount=None)

            payment = payment_service.generate_payment(device_token=device_token,
                                                       user_id=user_id,
                                                       order=order,
                                                       sender_id=hygge_booking_wallet,
                                                       receiver_id=hygge_mart_wallet)

            invoice_service.insert(user_id=user_id, order_id=order, payment=payment, comment=test_comment)
            LOG.info('refund done')

    def transfer_tokens_to_user(self, sender_user_id, sender_account_id, receiver_phone_number, amount, device_token):

        if amount < 1:
            raise InvalidParameterError(field_errors=[MissingFieldError(FieldErrors.Token)])

        wallets_repository = WalletsRepository()
        users_repository = UsersRepository()
        notification_factory = NotificationFactory()
        mobile_devices_repository = MobileDevicesRepository()
        notification_service = NotificationService()

        try:

            user = users_repository.fetch_by_phone_number(phone_number=receiver_phone_number, now=datetime_now())

            if UserGroupRelRepository().fetch_by_user_id(user_id=user.record_id, now=datetime_now()).group_id == 3:

                receiver_station = StationAssignmentRepository().fetch_by_user_record_id(now=datetime_now(),
                                                                                         user_id=user.record_id)
                receiver_id = receiver_station.station_record_id

                is_station_owner = True
            else:
                receiver_id = user.record_id
                is_station_owner = False

        except Exception:
            raise InvalidParameterError(field_errors=[InvalidFieldError(message=ErrorMessages.NotRegisteredUser.value,
                                                                        field=FieldErrors.PhoneNumber)])
        if is_station_owner:
            raise InvalidParameterError(description='This is not a valid EV Owner',
                                        field_errors=[InvalidFieldError(message=ErrorMessages
                                                                        .InvalidUserForTokenTransfer.value,
                                                                        field=FieldErrors.PhoneNumber)])

        sender_phone_number = users_repository.fetch_by_record_id(record_id=sender_user_id,
                                                                  now=datetime_now()).phone_number

        if receiver_phone_number == sender_phone_number:
            raise InvalidParameterError(field_errors=[InvalidFieldError(message=ErrorMessages.InvalidNumber.value,
                                                                        field=FieldErrors.PhoneNumber)])

        if (not user.verified) & (not is_station_owner):
            raise ConflictParameterError(field_errors=[InvalidFieldError(message=ErrorMessages.NotVerifiedUser.value,
                                                                         field=FieldErrors.PhoneNumber)])
        # todo test if station verified

        sender_wallet = wallets_repository.fetch_by_account_id(sender_account_id, datetime_now())
        LOG.info('sender record id %s' % sender_account_id)

        if sender_wallet.balance < amount:
            raise ConflictParameterError(
                field_errors=[InvalidFieldError(message=ErrorMessages.InsufficientBalance.value,
                                                field=FieldErrors.Balance)])

        receiver_wallet = wallets_repository.fetch_by_account_id(receiver_id, datetime_now())
        LOG.info('receiver record id %s' % receiver_id)

        self.transfer_tokens(sender_wallet, receiver_wallet, Decimal(amount))

        order_service = OrderService()
        order = order_service.generate_purchase_order(user_id=sender_user_id, amount=amount, from_unit='TOKEN',
                                                      to_unit='TOKEN', order_type=OrderTypes.TransferToken,
                                                      penalty_amount=None)

        payment_service = PaymentService()
        payment = payment_service.generate_payment(device_token=device_token,
                                                   user_id=sender_user_id,
                                                   order=order,
                                                   sender_id=sender_account_id,
                                                   receiver_id=receiver_id)

        invoice_service = InvoiceService()
        invoice_service.insert(user_id=sender_user_id, order_id=order, payment=payment, comment=test_comment)

        user = users_repository.fetch_by_record_id(record_id=user.record_id, now=datetime_now())
        device = mobile_devices_repository.fetch_by_user_phone_number(phone_number=user.phone_number)

        payments = {
            'payment': payment,
            'sender_id': sender_user_id
        }

        notification = notification_factory.create_and_queue_notification(data=payments, user_id=receiver_id,
                                                                          device=device,
                                                                          device_token=None,
                                                                          trigger='Token_transfer_receiver')

        notification_service.insert_notification(notifications=notification['notifications'],
                                                 to_device=notification['to_device'])

        return {}
