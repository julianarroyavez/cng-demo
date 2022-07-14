from app.errors import ForbiddenError
from app.log import LOG


def __get_required_permissions(required_authorizations):
    permissions = []
    for required_authorization in required_authorizations:
        for permission in required_authorization.permissions:
            permissions.append(permission.value + '-' + required_authorization.resource.value)

    return permissions


def authorize(req, resp, resource, params, required_authorizations):
    LOG.info('authorize params: %s' % required_authorizations)
    claims = req.context["auth_claims"]
    claims_permissions = claims.get('permissions')
    required_permissions = __get_required_permissions(required_authorizations)
    LOG.info('role: %s' % claims_permissions)

    for required_permission in required_permissions:
        LOG.info('required permission: %s' % required_permission)
        if claims_permissions is not None and required_permission not in claims_permissions:
            raise ForbiddenError(description="permission denied")
