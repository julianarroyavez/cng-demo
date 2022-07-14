import app.service.paytm_service as paytm_constant
from app.database import db_session
from app.domain.payment_schema import PaymentState, OrderTypes
from app.domain.resource_schema import StationAssignment
from app.errors import BalanceError, UserNotExistsError, ErrorMessages
from app.log import WALLET_LOG
from app.repository.payments_repository import PaymentsRepository
from app.repository.station_assignment_repository import StationAssignmentRepository
from app.repository.user_group_rel_repository import UserGroupRelRepository
from app.repository.wallets_repository import WalletsRepository
from app.service.invoice_service import InvoiceService
from app.service.order_service import OrderService
from app.service.payment_service import PaymentService
from app.service.paytm_service import PaytmService
from app.service.transaction_service import TransactionService
from app.util.datetime_util import datetime_now


class WalletService:
    def initiate_purchase(self, req_body, req_auth_claims, sender_id):
        with db_session.atomic():
            wallet_repository = WalletsRepository()
            hygge_mart_wallet = wallet_repository.fetch_hygge_mart_wallet()

            self.validate_purchase_request(req_body=req_body, hygge_mart_wallet=hygge_mart_wallet)

            order_service = OrderService()
            order = order_service.generate_purchase_order(user_id=req_auth_claims['user'],
                                                          amount=req_body['amount']['value'],
                                                          from_unit='INR',
                                                          to_unit='TOKEN',
                                                          order_type=OrderTypes.PayForToken,
                                                          penalty_amount=None)

            payment_service = PaymentService()
            payment = payment_service.generate_payment(device_token=req_body['context']['deviceToken'],
                                                       user_id=req_auth_claims['user'],
                                                       order=order,
                                                       sender_id=sender_id,
                                                       receiver_id=hygge_mart_wallet)

            invoice_service = InvoiceService()
            invoice_service.insert(user_id=req_auth_claims['user'],
                                   order_id=order,
                                   payment=payment,
                                   comment='Test Comment')

            paytm_service = PaytmService()
            gateway = paytm_service.initiate_txn(order=order)

            payment_service.init_success_update_database(payment=payment)

        return {
            "txnId": payment.id,
            "orderId": order.order_id,
            "status": "PROCESS_REQUIRED",
            "statusDesc": "txn initiated waiting for process",
            "orderAmount": {
                "value": float(order.total),
                "currency": "INR"
            },
            "gateway": {
                "mId": paytm_constant.MERCHANT_ID,
                "txnToken": gateway['body']['txnToken'],
                "callbackUrl": "https://securegw-stage.paytm.in/theia/paytmCallback?ORDER_ID=" + order.order_id,
                "paymentUrl": "https://securegw-stage.paytm.in/theia/api/v1/showPaymentPage"
            }
        }

    def verify_purchase(self, req, txn_id):
        paytm_service = PaytmService()
        payment_status_response = paytm_service.verify_txn(unique_order_id=req.context['data']['orderId'])

        transaction_service = TransactionService()
        response = transaction_service.final_payment_update(payment_status_response=payment_status_response, req=req)
        WALLET_LOG.info('verify purchase response: %s' % response)

        response['txnId'] = txn_id
        return response

    def embed_wallet(self, root_body, user_id, params):
        if UserGroupRelRepository().fetch_by_user_id(user_id=user_id, now=datetime_now()).group_id == 3:
            receiver_station = StationAssignmentRepository().fetch_by_user_record_id(now=datetime_now(),
                                                                                     user_id=user_id)
            account_id = receiver_station.station_record_id
        else:
            account_id = user_id
        wallet = self.get_wallet(account_id)

        root_body['_embedded'] = root_body.get('_embedded', {})
        root_body['_embedded']['wallet'] = wallet

    def get_wallet(self, account_id):
        wallet = WalletsRepository().fetch_by_account_id(account_id=account_id, now=datetime_now())

        return {
            "balance": float(wallet.balance),
            "name": wallet.name,
            "walletId": wallet.id
        }

    def validate_purchase_request(self, req_body, hygge_mart_wallet):
        # fetching hygge-mart balance
        hygge_mart_balance = hygge_mart_wallet.balance

        WALLET_LOG.info('Hygge Balance %s %s' % (hygge_mart_balance, req_body['amount']['value']))

        if hygge_mart_balance <= req_body['amount']['value']:
            raise BalanceError(description="Low balance")

    def init_failure_update_database(self, order_id):
        payment_repository = PaymentsRepository()

        new_payment = payment_repository.fetch_by_order_id(order_id=order_id)

        WALLET_LOG.info("current payment status %s" % new_payment.payment_status)

        new_payment.payment_status = PaymentState.GatewayInitFailed
        new_payment.save()

    def verification_failure_update_database(self, order_id):
        payment_repository = PaymentsRepository()

        new_payment = payment_repository.fetch_by_order_id(order_id=order_id)

        new_payment.payment_status = PaymentState.VerificationFailed
        new_payment.save()

    def encash_tokens(self, req_body, req_auth_claims, sender_id):

        now = datetime_now()

        try:
            station_wallet = WalletsRepository().fetch_by_account_id(account_id=sender_id, now=now)
            if station_wallet.balance < req_body['amount']['value']:
                raise BalanceError(message=ErrorMessages.InsufficientBalance.value,
                                   description="You don't have sufficient balance")
        except StationAssignment.DoesNotExist:
            raise UserNotExistsError(description="No station found for user")

        with db_session.atomic():
            order_service = OrderService()
            order = order_service.generate_purchase_order(user_id=req_auth_claims['user'],
                                                          amount=req_body['amount']['value'],
                                                          from_unit='TOKEN',
                                                          to_unit='TOKEN',
                                                          order_type=OrderTypes.EncashToken,
                                                          penalty_amount=None)

            hygge_mart_wallet = WalletsRepository().fetch_hygge_mart_wallet()
            payment_service = PaymentService()
            payment = payment_service.generate_payment_for_encashment(device_token=req_body['context']['deviceToken'],
                                                                      user_id=req_auth_claims['user'],
                                                                      order=order,
                                                                      sender_id=sender_id,
                                                                      receiver_id=hygge_mart_wallet)

            invoice_service = InvoiceService()
            invoice_service.insert(user_id=req_auth_claims['user'],
                                   order_id=order,
                                   payment=payment,
                                   comment='Test Comment')

            TransactionService().transit_tokens(sender_wallet=station_wallet, count_of_tokens=req_body['amount']['value'])

        return {
            "txnId": payment.id,
            "orderId": order.order_id,
            "status": "PROCESS_REQUIRED",
            "statusDesc": "txn initiated waiting for process",
            "orderAmount": {
                "value": float(order.total),
                "currency": "INR"
            }
        }





