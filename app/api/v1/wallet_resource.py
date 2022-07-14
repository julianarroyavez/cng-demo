import falcon
from app.errors import AppError, UnknownError
from app.hooks.authorization_hook import authorize
from app.log import LOG
from app.repository.station_assignment_repository import StationAssignmentRepository
from app.service.wallet_service import WalletService
from app.service.transaction_service import TransactionService
from app.service.payment_service import PaymentService
from app.api.common import BaseResource
from app.domain.auth_schema import Resources, PermissionScopes, Authorization, UserRoles
from app.util.datetime_util import datetime_now


class SelfPurchase(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.Wallets, [PermissionScopes.Update])])
    def on_post(self, req, res):
        try:
            if UserRoles.StationOwner.value in req.context['auth_claims']['role']:
                sender = StationAssignmentRepository().fetch_by_user_record_id(now=datetime_now(),
                                                                               user_id=req.context['auth_claims']['user'])
                sender_id = sender.station_record_id
            else:
                sender_id = req.context['auth_claims']['user']

            service = WalletService()
            body = service.initiate_purchase(req_body=req.context["data"],
                                             req_auth_claims=req.context['auth_claims'],
                                             sender_id=sender_id)

            self.on_success(res, status_code=falcon.HTTP_201, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='init failed', raw_exception=e))


class SelfPurchaseVerify(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.Wallets, [PermissionScopes.Update])])
    def on_post(self, req, res, txn_id):
        try:

            user_id = req.context['auth_claims']['user']
            device_token = req.context['auth_claims']['deviceToken']

            service = TransactionService()
            body = service.verify_purchase(req=req, txn_id=txn_id, user_id=user_id, device_token=device_token)

            self.embed_entities(req=req, res_body=body)

            self.on_success(res, status_code=falcon.HTTP_200, body=body)

        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='verification failed',
                                                                              raw_exception=e))


class Self(BaseResource):

    @falcon.before(authorize, [Authorization(resource=Resources.Wallets, permissions=[PermissionScopes.Retrieve])])
    def on_get(self, req, res):
        try:
            if UserRoles.StationOwner.value in req.context['auth_claims']['role']:
                sender_station = StationAssignmentRepository().fetch_by_user_record_id(now=datetime_now(),
                                                                                       user_id=req.context['auth_claims']['user'])
                account_id = sender_station.station_record_id
            else:
                account_id = req.context['auth_claims']['user']
            service = WalletService()
            body = service.get_wallet(account_id=account_id)

            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to fetch balance', raw_exception=e))


class Transaction(BaseResource):

    @falcon.before(authorize, [Authorization(resource=Resources.Wallets, permissions=[PermissionScopes.Retrieve])])
    def on_get(self, req, res):
        try:
            service = PaymentService()
            if req.params.get('offset') is None:
                req.params['offset'] = 0
            if req.params.get('limit') is None:
                req.params['limit'] = 10
            if req.params.get('transaction-type') is None:
                transaction_types = []
            else:
                transaction_types = req.params.get('transaction-type').split(',')

            if UserRoles.StationOwner.value in req.context['auth_claims']['role']:
                sender_station = StationAssignmentRepository().fetch_by_user_record_id(now=datetime_now(),
                                                                                       user_id=req.context['auth_claims']['user'])
                account_id = sender_station.station_record_id
            else:
                account_id = req.context['auth_claims']['user']

            body = service.get_transaction_history(account_id=str(account_id),
                                                   offset=req.params['offset'],
                                                   limit=req.params['limit'],
                                                   transaction_types=transaction_types)

            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to fetch balance', raw_exception=e))


class TransferTokens(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.Wallets, [PermissionScopes.Update])])
    def on_post(self, req, res):
        try:
            if UserRoles.StationOwner.value in req.context['auth_claims']['role']:
                sender_station = StationAssignmentRepository().fetch_by_user_record_id(now=datetime_now(),
                                                                                       user_id=req.context['auth_claims']['user'])
                sender_id = sender_station.station_record_id
            else:
                sender_id = req.context['auth_claims']['user']

            service = TransactionService()
            body = service.transfer_tokens_to_user(sender_user_id=req.context['auth_claims'].get('user'),
                                                   sender_account_id=sender_id,
                                                   receiver_phone_number=req.context['data']['receiver']['user']['phoneNumber'],
                                                   amount=req.context['data']['amount']['value'],
                                                   device_token=req.context['data']['context']['deviceToken'])

            self.embed_entities(req=req, res_body=body)
            self.on_success(res, status_code=falcon.HTTP_201, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='init failed', raw_exception=e))


class SelfEncash(BaseResource):

    @falcon.before(authorize, [Authorization(resource=Resources.Wallets, permissions=[PermissionScopes.Update])])
    def on_post(self, req, res):
        try:
            if UserRoles.StationOwner.value in req.context['auth_claims']['role']:
                sender_station = StationAssignmentRepository().fetch_by_user_record_id(now=datetime_now(),
                                                                                       user_id=req.context['auth_claims']['user'])
                sender_id = sender_station.station_record_id
            else:
                sender_id = req.context['auth_claims']['user']

            service = WalletService()
            body = service.encash_tokens(req_body=req.context["data"],
                                         req_auth_claims=req.context['auth_claims'],
                                         sender_id=sender_id)

            self.embed_entities(req=req, res_body=body)
            self.on_success(res, status_code=falcon.HTTP_201, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='encash failed', raw_exception=e))




