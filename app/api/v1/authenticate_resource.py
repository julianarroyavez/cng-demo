import falcon
from app.errors import AppError, UnknownError, InvalidParameterError, InvalidFieldError, MissingFieldError, FieldErrors
from app.api.common import BaseResource
from app.service.authentication_service import AuthenticationService, AuthenticationState
from app.service.token_service import decode_token
from app.log import LOG


class Collection(BaseResource):

    def on_post(self, req, res):
        """
        to process initial authentication request and resent request
        """
        try:
            service = AuthenticationService()
            req_body = req.context['data']

            if req_body.get('verificationFactor') == 'otp':
                body = service.request_otp(req_body)
            elif req_body.get('verificationFactor') == 'token':
                body = service.handle_refresh_token_request(req_body)
            else:
                raise InvalidParameterError(field_errors=[InvalidFieldError(FieldErrors.VerificationFactor)])

            status_code = falcon.HTTP_201 if body['status'] == AuthenticationState.OtpRequired.value else falcon.HTTP_200
            self.on_success(res, status_code=status_code, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to send otp', raw_exception=e))


class ItemVerify(BaseResource):

    def on_post(self, req, res, txn_id_path):
        try:
            service = AuthenticationService()
            body = service.verify_otp(req_body=req.context['data'], txn_id=txn_id_path)
            try:
                req.context["auth_claims"] = decode_token(body['sessionToken'], verify_expiry=False)
                self.embed_entities(req, body)
            except Exception as e:
                LOG.error('failed to embed at outer layer | %s' % e)
            self.on_success(res, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to verify otp', raw_exception=e))

