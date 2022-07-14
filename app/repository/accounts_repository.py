from app.domain.auth_schema import Accounts


class AccountsRepository:

    def insert(self, primary_key, record_id, alias_name, creator_user_id, now, type):
        return (Accounts
                .create(id=primary_key,
                        record_id=record_id,
                        alias_name=alias_name,
                        created_on=now,
                        modified_on=now,
                        validity_start=now,
                        created_by=creator_user_id,
                        modified_by=creator_user_id,
                        type=type))
