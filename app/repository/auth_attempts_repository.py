from app.domain.auth_schema import AuthAttempts


class AuthAttemptsRepository:
    def fetch_all_previous_records_for_user(self, phone_number, device_token, records_after_time):
        return AuthAttempts.select().where(
            ((AuthAttempts.phone_number == phone_number)
            | (AuthAttempts.device_token == device_token))
            & (AuthAttempts.modified_on > records_after_time)
        ).order_by(AuthAttempts.modified_on.desc())

    def fetch_by_txn_id(self, txn_id):
        return AuthAttempts.get(AuthAttempts.txn_id == txn_id)

    def insert(self, txn_id, device_token, country_code, phone_number, otp, state, state_desc,
               backing_txn_id, audit_user):
        return AuthAttempts.create(
            txn_id=txn_id,
            device_token=device_token,
            country_code=country_code,
            phone_number=phone_number,
            active=True,
            otp=otp,
            state=state,
            state_desc=state_desc,
            verification_attempt_count=0,
            backing_txn_id=backing_txn_id,
            created_by=audit_user,
            modified_by=audit_user
        )

    def update(self, record, modified_on=None):
        record.modified_on = modified_on
        record.save()
