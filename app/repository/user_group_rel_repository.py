from app.database import db_session
from app.domain.auth_schema import Groups, UserRoles, UserGroupRel


class UserGroupRelRepository:

    def fetch_by_user_id(self, user_id, now):
        return UserGroupRel.select().where((UserGroupRel.validity_start <= now)
                                           & (UserGroupRel.validity_end > now)
                                           & (UserGroupRel.user == user_id)).get()

    def update_to_end_validity(self, record, audit_user_id, now, validity_end):
        record.modified_on = now
        record.modified_by = audit_user_id
        record.validity_end = validity_end
        record.save()

    def __insert(self, user, group):
        return UserGroupRel.create(
            created_by=user,
            modified_by=user,
            user_record_id=user,
            group_id=group
        )

    def insert_as_guest(self, user):
        guest_group = (Groups.get(Groups.name == UserRoles.Guest.value))
        return self.__insert(user=user.record_id, group=guest_group)

    def update_to_ev_owner(self, user, now):
        with db_session.atomic():
            existing_mapping = self.fetch_by_user_id(user_id=user.record_id, now=now)
            self.update_to_end_validity(record=existing_mapping, audit_user_id=user.record_id, now=now, validity_end=now)
            ev_owner_group = (Groups.get(Groups.name == UserRoles.EvOwner.value))
            self.__insert(user=user.record_id, group=ev_owner_group)

    def update_to_evs_owner(self, user, now):
        with db_session.atomic():
            existing_mapping = self.fetch_by_user_id(user_id=user.get('user'), now=now)
            self.update_to_end_validity(record=existing_mapping, audit_user_id=user.get('user'), now=now, validity_end=now)
            ev_owner_group = (Groups.get(Groups.name == UserRoles.StationOwner.value))
            self.__insert(user=user.get('user'), group=ev_owner_group)
