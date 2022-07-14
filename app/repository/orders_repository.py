from app.domain.payment_schema import Orders


class OrdersRepository:
    def insert(self, order_id, user_id, amount_in_inr, order_status, order_type):
        return (Orders
                .create(order_id=order_id,
                        created_by=user_id,
                        modified_by=user_id,
                        order_summary=None,
                        total=amount_in_inr,
                        order_status=order_status,
                        order_type=order_type))

    def fetch_by_order_id(self, order_id):  # todo: avoid payment fetch using order id
        return (Orders
                .select()
                .where(Orders.order_id == order_id)
                .get())

    def update(self, record):
        return (record
                .save())
