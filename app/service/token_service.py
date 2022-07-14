import datetime

import jwt
from jwt import ExpiredSignatureError

from app import config
from app.domain.auth_schema import Users, UserGroupRel, Groups, GroupRoleRel, Roles, RolePermissionRel, Permissions, \
    PermissionScopes
from app.log import LOG
from app.repository.station_assignment_repository import StationAssignmentRepository
from app.repository.user_group_rel_repository import UserGroupRelRepository
from app.util.datetime_util import datetime_now, after_now, current_time_millis
from app.util.json_util import UUIDEncoder

__SessionTokenSecret = config.SESSION['session_token_secret']
__SessionValidityInHours = int(config.SESSION['session_validity_in_hours'])
__SessionValidityInHoursRefreshToken = int(config.SESSION['session_validity_in_hours_refresh_token'])


def issue_new_token(valid_auth_attempt, session_user):

    user_group_rel_repository = UserGroupRelRepository()

    try:
        user_group_rel_repository.fetch_by_user_id(
            user_id=session_user.record_id,
            now=datetime_now()
        )
    except Exception:
        UserGroupRelRepository().insert_as_guest(session_user)

    station_id = None

    if session_user.type is not None:
        try:
            station = StationAssignmentRepository().fetch_by_user_record_id(now=datetime_now(),
                                                                            user_id=session_user.record_id)

            station_id = station.station_record_id
        except Exception as e:
            LOG.error('Station does not exists for this user with error %s' % e)

    roles = set([])
    permissions = set([])
    now = datetime_now()
    query = (Groups.select(Roles.name,
                           Permissions.resource_name,
                           Permissions.can_create,
                           Permissions.can_retrieve,
                           Permissions.can_update,
                           Permissions.can_delete,
                           Permissions.can_search)
             .join_from(Groups, GroupRoleRel, on=(Groups.id == GroupRoleRel.group), attr='group_role_rel')
             .join_from(GroupRoleRel, Roles, on=(GroupRoleRel.role == Roles.id), attr='role')
             .join_from(Roles, RolePermissionRel, on=(Roles.id == RolePermissionRel.role), attr='role_permission_rel')
             .join_from(RolePermissionRel, Permissions, on=(RolePermissionRel.permission == Permissions.id),
                        attr='permission')
             .join_from(Groups, UserGroupRel, on=(Groups.id == UserGroupRel.group_id))
             .where((UserGroupRel.user == session_user.record_id)
                    & (UserGroupRel.validity_start <= now)
                    & (UserGroupRel.validity_end > now)))
    for rec in query:
        LOG.info('query output is %s and %s' % (rec.group_role_rel.role.name.value, rec.group_role_rel.role.role_permission_rel.permission.name))
        roles.add(rec.group_role_rel.role.name.value)
        permissions.update(resolve_permission(rec.group_role_rel.role.role_permission_rel.permission))

    LOG.info('roles -- %s' % roles)
    LOG.info('permissions -- %s' % permissions)
    LOG.info('record id %s' % session_user.record_id)
    payload = {
        "iat": datetime.datetime.utcnow(),  # issued_at
        "exp": after_now(hours=__SessionValidityInHours),  # expiration_time
        "jti": valid_auth_attempt.txn_id,  # unique_identifier
        "deviceToken": valid_auth_attempt.device_token,
        "user": session_user.record_id,
        "role": list(roles),
        "permissions": list(permissions)
    }
    if station_id is not None:
        payload["station_id"] = station_id

    return jwt.encode(payload, __SessionTokenSecret, algorithm="HS256", json_encoder=UUIDEncoder)


def decode_token(jwt_token, verify_expiry=True):
    return jwt.decode((jwt_token + '=' * (-len(jwt_token) % 4)), __SessionTokenSecret, algorithms=["HS256"],
                      options={"verify_exp": verify_expiry})


def resolve_permission(permission):
    permissions = []
    if permission.can_create:
        permissions.append(PermissionScopes.Create.value + '-' + permission.resource_name)
    if permission.can_retrieve:
        permissions.append(PermissionScopes.Retrieve.value + '-' + permission.resource_name)
    if permission.can_update:
        permissions.append(PermissionScopes.Update.value + '-' + permission.resource_name)
    if permission.can_delete:
        permissions.append(PermissionScopes.Delete.value + '-' + permission.resource_name)
    if permission.can_search:
        permissions.append(PermissionScopes.Search.value + '-' + permission.resource_name)
    return permissions


def issue_refresh_token(valid_auth_attempt):
    now = datetime_now()
    session_user = (Users
                    .get((Users.phone_number == valid_auth_attempt.phone_number)
                         & (Users.validity_start <= now)
                         & (Users.validity_end > now)))

    payload = {
        "iat": datetime.datetime.utcnow(),  # issued_at
        "exp": after_now(hours=__SessionValidityInHoursRefreshToken),  # expiration_time
        "jti": valid_auth_attempt.txn_id,  # unique_identifier
        "deviceToken": valid_auth_attempt.device_token,
        "user": session_user.record_id,
        "phoneNumber": valid_auth_attempt.phone_number
    }
    return jwt.encode(payload, __SessionTokenSecret, algorithm="HS256", json_encoder=UUIDEncoder)


def validate_token_claims(claims):
    if claims is None:
        raise ExpiredSignatureError()

    LOG.info('claims time ' + str(claims.get('exp')))
    LOG.info('current time ' + str(current_time_millis()))
    if claims.get('user') is None or current_time_millis() > claims.get('exp') * 1000:
        raise ExpiredSignatureError()
