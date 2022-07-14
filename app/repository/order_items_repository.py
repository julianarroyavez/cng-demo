from app.domain.payment_schema import OrderItems
from app.log import LOG


class OrderItemsRepository:

    def __init__(self):
        pass  # empty is required

    def insert(self, user_id, rate, rate_id, quantity, amount_in_inr, order_id, service_rate_table_id=None,
               days_of_week=None, segments_of_day=None, service_master_id=None, rated_power_id=None):
        return (OrderItems
                .create(created_by=user_id,
                        modified_by=user_id,
                        item="token purchase",
                        item_rate=rate,
                        applied_token_rate=rate_id,
                        quantity=quantity,
                        total=amount_in_inr,
                        order_id=order_id,
                        attrs={'service_rate_table_id': service_rate_table_id, 'days_of_week': days_of_week,
                               'segments_of_day': segments_of_day, 'service_master_id': service_master_id,
                               'rated_power_id': rated_power_id}))

    def fetch_by_order_id(self, order_id):
        return (OrderItems
                .select()
                .where(OrderItems.order_id == order_id)
                .get())
