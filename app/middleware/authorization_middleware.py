from jwt import ExpiredSignatureError

from app.errors import UnauthorizedError
from app.log import LOG
from app.service.token_service import decode_token
from app.service import token_service

ignore_list = [
    '/api/v1/authn'
]


class AuthorizationMiddleware(object):

    def process_request(self, req, resp):
        LOG.debug("Authorization: %s", req.auth)
        if req.auth is not None:
            try:
                claims = decode_token(str.replace(str(req.auth), 'Bearer ', ''))
                token_service.validate_token_claims(claims)

                req.context["auth_claims"] = claims
                LOG.info('user: %s' % claims.get('user'))
            except ExpiredSignatureError:
                raise UnauthorizedError(description="Token expired")
        else:
            req.context["auth_claims"] = None

    def process_resource(self, req, resp, resource, params):
        pass  # empty is required

    def process_response(self, req, resp, resource, req_succeeded):
        pass  # empty is required




