import falcon
from app.errors import AppError, UnknownError
from app.hooks.authorization_hook import authorize
from app.service.user_service import UserService
from app.api.common import BaseResource
from app.domain.auth_schema import Resources, PermissionScopes, Authorization
from app.log import LOG


class Collection(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.Users, [PermissionScopes.Update])])
    def on_post(self, req, res):
        try:
            service = UserService()
            if req.params.get('account-type') == 'evo':
                body = service.evo_user_registration(req_body=req.context['data'], req_file=req.context['file'],
                                                     req_auth_claims=req.context['auth_claims'])

            elif req.params.get('account-type') == 'evso':
                body = service.evso_user_registration(req_body=req.context['data'],
                                                      req_auth_claims=req.context['auth_claims'])

            elif req.params.get('account-type') == 'cngvo':
                file = req.context['file'] if 'file' in req.context else None
                body = service.cng_vo_user_registration(req_body=req.context['data'],
                                                        req_auth_claims=req.context['auth_claims'], req_file=file)

            self.on_success(res, status_code=falcon.HTTP_201, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to register',
                                                                              raw_exception=e))

    @falcon.before(authorize, [Authorization(Resources.Users, [PermissionScopes.Retrieve])])
    def on_get(self, req, res):
        try:
            service = UserService()
            body = service.get_evo_details(role_type=req.params.get('role-type', None),
                                           phone_number=req.params.get('phone-number', None))

            for i in range(len(body['users'])):
                self.embed_entities(req, body,
                                    user_extractor=lambda req_body, res_body, value=i: res_body['users'][value].get(
                                        'id'))

            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to get user details',
                                                                              raw_exception=e))


class ItemVerify(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.Users, [PermissionScopes.Update])])
    def on_post(self, req, res, user_id):
        try:
            service = UserService()
            body = service.verify_user(req_body=req.context['data'], req_auth_claims=req.context['auth_claims'])
            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to verify user',
                                                                              raw_exception=e))


class ItemDLImage(BaseResource):

    @falcon.before(authorize, [Authorization(resource=Resources.Users, permissions=[PermissionScopes.Retrieve])])
    def on_get(self, req, res, user_id):
        try:
            service = UserService()
            body = service.get_users_dl_image(user_id=user_id, size=req.params.get('size', None))

            self.on_image_success(res=res, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to get DL image',
                                                                              raw_exception=e))


class ItemProfileImage(BaseResource):

    @falcon.before(authorize, [Authorization(resource=Resources.Users, permissions=[PermissionScopes.Retrieve])])
    def on_get(self, req, res, user_id):
        try:
            service = UserService()
            body = service.get_users_profile_image(user_id=user_id, size=req.params.get('size', None))

            self.on_image_success(res=res, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description='failed to get profile image',
                                                                              raw_exception=e))


class Self(BaseResource):

    @falcon.before(authorize, [Authorization(Resources.Users, [PermissionScopes.Retrieve])])
    def on_get(self, req, res):
        try:
            service = UserService()
            body = service.get_user_profile(req_auth_claims=req.context['auth_claims'])
            self.embed_entities(req, body)

            self.on_success(res, status_code=falcon.HTTP_200, body=body)
        except Exception as e:
            self.on_error(res, e if isinstance(e, AppError) else UnknownError(description="failed to get User's data",
                                                                              raw_exception=e))
