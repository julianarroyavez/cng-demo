import operator
import uuid
from functools import reduce

from app.domain.support.support_schema import SupportQueries, SupportQueryStatus
from app.log import LOG


class SupportQueryRepository:
    def insert(self, query_dto, now, user_id=None):
        return SupportQueries.create(
            id=str(uuid.uuid4()),
            created_by=user_id,
            modified_by=user_id,
            customer_email=query_dto.customer_email,
            customer_phone=query_dto.customer_phone,
            query_text=query_dto.query_text,
            customer_device_token=query_dto.context.device_token,
            customer_device_os_version=query_dto.context.device_os_version,
            customer_app_version=query_dto.context.app_version,
            session_token=query_dto.context.session_token,
            customer_user=user_id,
            query_date=now,
            status=SupportQueryStatus.Open
        )

    def fetch_all_active(self, all_active_status, columns, where_clauses_query_field, where_clauses_date_range,
                         sort=None, limit=500, offset=0):
        query_data = (SupportQueries.select(*columns)
                      .where(reduce(operator.or_, where_clauses_query_field)
                             & (reduce(operator.and_, where_clauses_date_range))
                             & (SupportQueries.status.in_(all_active_status))).limit(limit).offset(offset)
                      )
        if sort:
            for sort_column in sort:
                data = sort_column.split('-')
                try:
                    sort_direction = data[1]
                except Exception:
                    sort_direction = 'asc'
                field = getattr(SupportQueries, data[0])
                if sort_direction != 'asc':
                    field = field.desc()
                query_data = query_data.order_by(field)
            #  .order_by(SupportQueries.modified_on.desc(), SupportQueries.status))
        return query_data

    def find_by_id(self, query_id):
        return (SupportQueries.select()
                .where(SupportQueries.id == query_id)
                .get())

    def update(self, query_dto, now, query_id, user_id=None):
        return (SupportQueries.update(
            modified_by=user_id,
            modified_on=now,
            status=query_dto.status,
            response_comment=query_dto.response_comment,
            response_date=query_dto.response_date,
            response_by=user_id
        )
                .where(SupportQueries.id == query_id)
                .execute())