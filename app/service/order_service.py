from decimal import Decimal

from app.domain.payment_schema import OrderTypes
from app.log import LOG
from app.repository.order_items_repository import OrderItemsRepository
from app.repository.orders_repository import OrdersRepository
from app.repository.token_conversion_rates_repository import TokenConversionRatesRepository
from app.util.datetime_util import datetime_now
from app.util.string_util import generate_key


class OrderService:
    def generate_purchase_order(self, user_id, amount, from_unit, to_unit, order_type, penalty_amount,
                                service_rate_table_id=None, days_of_week=None, segments_of_day=None,
                                service_master_id=None, rated_power_id=None):
        token_conversion_rates_repository = TokenConversionRatesRepository()
        orders_repository = OrdersRepository()
        order_items_repository = OrderItemsRepository()
        now = datetime_now()

        # fetching conversion rate
        current_rate = token_conversion_rates_repository.fetch_by_unit(from_unit=from_unit,
                                                                       to_unit=to_unit, now=now)

        amount_in_inr = Decimal(amount) * Decimal(current_rate.conversion_rate)
        LOG.info('Total Amount %s' % amount_in_inr)

        if penalty_amount is not None and penalty_amount != 0:
            penalty_amount = -1 * penalty_amount
            penalty_amount_in_inr = Decimal(penalty_amount) * Decimal(current_rate.conversion_rate)
            total_amount_in_inr = amount_in_inr + penalty_amount_in_inr
        else:
            total_amount_in_inr = amount_in_inr

        order_id = generate_key(key_length=15)

        # todo: bring status from the enums
        newly_created_order = orders_repository.insert(order_id=order_id, user_id=user_id,
                                                       amount_in_inr=total_amount_in_inr, order_status='SUCCESS', order_type=order_type)

        # order_item_id = OrderItems.select().order_by(OrderItems.id.desc()).get().id + 1
        # [ERROR] duplicate key value
        # violates unique constraint "order_items_pkey" DETAIL:  Key (id)=(2) already exists.

        order_items_repository.insert(user_id, current_rate.conversion_rate, current_rate, amount, amount_in_inr,
                                      order_id, service_rate_table_id, days_of_week, segments_of_day, service_master_id,
                                      rated_power_id)

        if penalty_amount is not None and penalty_amount != 0:
            order_items_repository.insert(user_id, current_rate.conversion_rate,
                                          current_rate, penalty_amount,
                                          penalty_amount_in_inr,
                                          order_id, service_rate_table_id, days_of_week, segments_of_day)

        return newly_created_order

    def generate_purchase_order_tokens(self, order):

        orders_repository = OrdersRepository()
        order_items_repository = OrderItemsRepository()
        order_id = generate_key(key_length=15)
        newly_created_order = orders_repository.insert(order_id=order_id, user_id=order.created_by, amount_in_inr=order.total, order_status='SUCCESS', order_type=OrderTypes.PurchaseToken)

        order_item = order_items_repository.fetch_by_order_id(order.order_id)

        order_items_repository.insert(order_item.created_by, order_item.item_rate,
                                      order_item.applied_token_rate, order_item.quantity,
                                      order_item.total,
                                      order_id)

        return newly_created_order





