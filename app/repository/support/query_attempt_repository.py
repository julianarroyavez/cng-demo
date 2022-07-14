from peewee import fn

from app.domain.support.support_schema import QueryAttempts
from app.log import LOG


class QueryAttemptRepository:
    def insert(self, query_attempt_dto, user_id=None):
        LOG.info(type(query_attempt_dto.phone_number))
        return QueryAttempts.create(
            id=fn.nextval('query_attempts_id_seq'),
            phone_number=query_attempt_dto.phone_number,
            device_token=query_attempt_dto.device_token,
            state=query_attempt_dto.state,
            state_desc=query_attempt_dto.state_desc,
            created_by=user_id,
            modified_by=user_id
        )

    def fetch_by_device_token_and_date(self, device_token, records_after_time):
        return (QueryAttempts
                .select().distinct()
                .where((QueryAttempts.device_token == device_token)
                       & (QueryAttempts.created_on > records_after_time))).count()
