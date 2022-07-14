from app.domain.auth_schema import Permissions
from app.repository.permissions_repository import PermissionsRepository


class PermissionsService:

    def embed_permissions(self, root_body, user_id, params):
        permissions = []
        permissions_repository = PermissionsRepository()

        columns = [Permissions.resource_name, Permissions.can_search, Permissions.can_retrieve,
                   Permissions.can_update, Permissions.can_create, Permissions.can_delete]

        for permission in params['permissions'].split(','):
            result = permissions_repository.get_permissions_by_name(name=permission, columns=columns)

            permissions.append({
                "resourceName": result.resource_name,
                "canRetrieve": result.can_retrieve,
                "canSearch": result.can_search,
                "canCreate": result.can_create,
                "canUpdate": result.can_update,
                "canDelete": result.can_delete
            })

        if root_body.get('_embedded', None) is None:
            root_body['_embedded'] = {
                'permissions': permissions
            }
        else:
            root_body['_embedded']['permissions'] = permissions
        return root_body
