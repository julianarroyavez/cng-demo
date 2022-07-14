from app.domain.auth_schema import Permissions


class PermissionsRepository:

    def get_permissions_by_name(self, name, columns):
        return (Permissions
                .select(*columns)
                .where(Permissions.resource_name == name)
                .get()
                )
