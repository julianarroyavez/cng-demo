from peewee import fn
import uuid

from app.database import db_session
from app.domain.auth_schema import Users, UserGroupRel, Roles, AccountType
from app.log import LOG
from app.repository.accounts_repository import AccountsRepository
from app.repository.wallets_repository import WalletsRepository


class UsersRepository:
    def validate_by_dl_number(self, dl_number):
        query = (Users
                 .select()
                 .where(fn.Lower(Users.licence_number) == dl_number.lower()))
        return query.exists()

    def fetch_by_record_id(self, record_id, now):
        return (Users
                .select()
                .where((Users.record_id == record_id)
                       & (Users.validity_start <= now)
                       & (Users.validity_end > now))
                .get())

    def fetch_by_name(self, name, now):
        return (Users
                .select()
                .where((Users.validity_start <= now)
                       & (Users.validity_end >= now)
                       & (Users.name == name))
                .get())

    def fetch_prospect_user(self, now):
        return self.fetch_by_name('prospect-user', now=now)

    def fetch_by_phone_number(self, phone_number, now):
        return (Users
                .get((Users.phone_number == phone_number)
                     & (Users.validity_start <= now)
                     & (Users.validity_end > now)))

    def fetch_all_by_phone_number_and_role(self, phone_number, now, role):
        return (Users
                .select()
                .join_from(Users, UserGroupRel, on=(Users.record_id == UserGroupRel.user_record_id))
                .join_from(UserGroupRel, Roles, on=(UserGroupRel.group_id == Roles.id))
                .where((Roles.name == role)
                       & (Users.phone_number == phone_number)
                       & (Users.validity_start <= now)
                       & (Users.validity_end > now)))

    def fetch_dl_image_by_record_id(self, user_id, now):
        return (Users
                .select(Users.licence_image)
                .where((Users.record_id == user_id)
                       & (Users.validity_start <= now)
                       & (Users.validity_end > now))
                .get()
                .licence_image)

    def fetch_profile_image_by_record_id(self, user_id, now):
        return (Users
                .select(Users.profile_image)
                .where((Users.record_id == user_id)
                       & (Users.validity_start <= now)
                       & (Users.validity_end > now))
                .get()
                .profile_image)

    def insert(self, phone_number):
        primary_key = str(uuid.uuid4())
        with db_session.atomic():
            newly_added_user = (Users
                                .create(id=primary_key,
                                        record_id=primary_key,
                                        customer_id=primary_key,
                                        phone_number=phone_number,
                                        created_by=primary_key,
                                        modified_by=primary_key,
                                        type=AccountType.User))

            AccountsRepository().insert(primary_key=primary_key,
                                        record_id=primary_key,
                                        alias_name='user_{}'.format(phone_number),
                                        creator_user_id=primary_key,
                                        now=newly_added_user.validity_start,
                                        type=AccountType.User)

            wallet_key = str(uuid.uuid4())
            WalletsRepository().insert(primary_key=wallet_key,
                                       record_id=wallet_key,
                                       name='user_wallet_{}'.format(phone_number),
                                       account_id=primary_key,
                                       creator_user_id=primary_key,
                                       now=newly_added_user.validity_start)

            return newly_added_user

    def update_temporal_record(self,
                               record_id,
                               phone_number,
                               name,
                               email,
                               pin_code,
                               licence_number,
                               licence_number_image,
                               primary_key,
                               now,
                               mileage_card_number):
        with db_session.atomic():
            try:
                # todo: can be merge into single update query
                existing_user = self.fetch_by_record_id(record_id=record_id, now=now)

                self.update_with_validity_end(
                    record=existing_user,
                    audit_user=record_id,
                    now=now,
                    validity_end=now
                )
            except Exception as e:
                LOG.error(e)

            return Users.create(
                id=primary_key,
                phone_number=phone_number,
                record_id=record_id or primary_key,
                customer_id=record_id or primary_key,
                validity_start=now,
                name=name,
                email=email,
                pin_code=pin_code,
                licence_image=licence_number_image.read() if licence_number_image is not None else None,
                licence_number=licence_number,
                created_by=record_id or primary_key,
                modified_by=record_id or primary_key,
                type=AccountType.User,
                mileage_card_number=mileage_card_number
            )

    def update_with_validity_end(self, record, audit_user, now, validity_end):
        record.modified_on = now
        record.modified_by = audit_user
        record.validity_end = validity_end
        record.save()

    def validate_by_phone_number(self, phone_number, now, role):
        query = (Users
                 .select()
                 .join_from(Users, UserGroupRel, on=(Users.record_id == UserGroupRel.user_record_id))
                 .join_from(UserGroupRel, Roles, on=(UserGroupRel.group_id == Roles.id))
                 .where((Roles.name != role)
                        & (Users.phone_number == phone_number)
                        & (Users.validity_start <= now)
                        & (Users.validity_end > now)))
        return query.exists()

    def update_verified_state(self, user, verified):
        user.verified = verified
        user.save()

    def fetch_all_by_validity(self, now):
        return (Users
                .select()
                .where((Users.validity_start <= now)
                       & (Users.validity_end > now)))

    def fetch_all_details_with_role_by_record_id(self, columns, record_id, now):
        return (Users
                .select(*columns)
                .join_from(Users, UserGroupRel, attr='user_group_rel',
                           on=(Users.record_id == UserGroupRel.user_record_id))
                .join_from(UserGroupRel, Roles, attr='roles',
                           on=(UserGroupRel.group_id == Roles.id))
                .where((Users.record_id == record_id)
                       & (Users.validity_start <= now)
                       & (Users.validity_end > now)
                       & (UserGroupRel.validity_start <= now)
                       & (UserGroupRel.validity_end > now))
                .get())

    def update_evso_temporal_record(self, record_id, phone_number, primary_key, now):
        with db_session.atomic():
            try:
                # todo: can be merge into single update query
                existing_user = self.fetch_by_record_id(record_id=record_id, now=now)

                self.update_with_validity_end(
                    record=existing_user,
                    audit_user=record_id,
                    now=now,
                    validity_end=now
                )
            except Exception as e:
                LOG.error(e)

            return Users.create(
                id=primary_key,
                phone_number=phone_number,
                record_id=record_id or primary_key,
                customer_id=record_id or primary_key,
                validity_start=now,
                created_by=record_id or primary_key,
                modified_by=record_id or primary_key,
                type=AccountType.Station
            )

    def fetch_license_by_id(self, user_id, now):
        return (Users
                .select(Users.licence_number)
                .where((Users.record_id == user_id)
                       & (Users.validity_start <= now)
                       & (Users.validity_end > now))
                .get()
                .licence_number)
