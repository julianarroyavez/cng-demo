from app.domain.payment_schema import Payments, Wallets, Orders, Invoices, OrderTypes
from app.domain.auth_schema import Accounts, Users
from peewee import JOIN
import operator
from functools import reduce

from app.domain.resource_schema import Stations


class PaymentsRepository:
    def fetch_by_order_id(self, order_id):  # todo: avoid payment fetch using order id
        return Payments.select().where(
            Payments.order_id == order_id
        ).order_by(Payments.modified_on.desc()).get()

    def insert(self, payment_id, user_id, order_id, sender_id, receiver_id, total_amount, today, payment_status,
               device_id, gateway_name):
        return Payments.create(
            id=payment_id,
            created_by=user_id,
            modified_by=user_id,
            order_id=order_id,
            sender=sender_id,
            receiver=receiver_id,
            order_amount=total_amount,
            order_date=today,  # todo to get date from datetime util
            payment_status=payment_status,
            device_id=device_id,
            gateway_name=gateway_name
        )

    def update(self, record):
        return record.save()

    def fetch_payments(self, account_id, offset, limit, transaction_types):
        sender_account = Accounts.alias()
        sender_wallet = Wallets.alias()
        sender_user = Users.alias()
        sender_station = Stations.alias()
        receiver_account = Accounts.alias()
        receiver_wallet = Wallets.alias()
        receiver_user = Users.alias()
        receiver_station = Stations.alias()

        on_clauses = []
        where_clauses = []
        if not transaction_types:
            on_clauses.append(Orders.order_type == OrderTypes.PurchaseToken)
            on_clauses.append(Orders.order_type == OrderTypes.PayForBooking)
            on_clauses.append((Orders.order_type == OrderTypes.PayForToken) & (
                    (Orders.order_status == 'FAILURE') | (Orders.order_status == 'CANCELLED')))
            on_clauses.append(Orders.order_type == OrderTypes.TransferToken)
            on_clauses.append(Orders.order_type == OrderTypes.CancelBooking)
            on_clauses.append(Orders.order_type == OrderTypes.EncashToken)
            where_clauses.append(sender_account.id == account_id)
            where_clauses.append(receiver_account.id == account_id)

        if 'CREDIT' in transaction_types:
            on_clauses.append(Orders.order_type == OrderTypes.PurchaseToken)
            on_clauses.append(Orders.order_type == OrderTypes.CancelBooking)
            on_clauses.append(Orders.order_type == OrderTypes.TransferToken)
            where_clauses.append((((Orders.order_type == OrderTypes.PurchaseToken) & (receiver_account.id == account_id)) |
                                  ((Orders.order_type == OrderTypes.TransferToken) & (receiver_account.id == account_id)) |
                                  ((Orders.order_type == OrderTypes.CancelBooking) & (sender_account.id == account_id))))

        if 'DEBIT' in transaction_types:
            on_clauses.append(Orders.order_type == OrderTypes.PayForBooking)
            on_clauses.append(Orders.order_type == OrderTypes.EncashToken)
            on_clauses.append(Orders.order_type == OrderTypes.TransferToken)
            where_clauses.append(where_clauses.append(sender_account.id == account_id))

        if 'CREDIT_FAILURE' in transaction_types:
            on_clauses.append((Orders.order_type == OrderTypes.PayForToken) & (
                        (Orders.order_status == 'FAILURE') | (Orders.order_status == 'CANCELLED')))
            where_clauses.append(where_clauses.append(sender_account.id == account_id))

        return (Payments.select(Payments.id, Payments.payment_status, Payments.modified_on, Payments.comment, Payments.order_amount,
                                Orders.order_id, Orders.order_status, Orders.order_type, Orders.total, Invoices.id,
                                sender_account.record_id, sender_account.alias_name, sender_wallet.record_id, sender_wallet.name,
                                sender_user.record_id, sender_user.customer_id, sender_user.phone_number, sender_user.name, sender_user.verified,
                                receiver_account.record_id, receiver_account.alias_name, receiver_wallet.record_id, receiver_wallet.name,
                                receiver_user.record_id, receiver_user.customer_id, receiver_user.phone_number, receiver_user.name, receiver_user.verified,
                                sender_station.record_id, sender_station.verified, receiver_station.record_id, receiver_station.verified
                                )
                .join_from(Payments, Orders, attr='order', on=((Payments.order == Orders.order_id) &
                                                               reduce(operator.or_, on_clauses)))
                .join_from(Payments, Invoices, attr='invoices', on=(Invoices.payment == Payments.id))
                .join_from(Payments, sender_account, attr='sender_account', on=(Payments.sender == sender_account.record_id))
                .join_from(sender_account, sender_wallet, attr='sender_wallet', on=(sender_account.record_id == sender_wallet.account))
                .join_from(sender_account, sender_user, JOIN.LEFT_OUTER, attr='sender_user', on=(sender_account.record_id == sender_user.id))
                .join_from(sender_account, sender_station, JOIN.LEFT_OUTER, attr='sender_station', on=(sender_account.record_id == sender_station.id))
                .join_from(Payments, receiver_account, attr='receiver_account', on=(Payments.receiver == receiver_account.record_id))
                .join_from(receiver_account, receiver_wallet, attr='receiver_wallet', on=(receiver_account.record_id == receiver_wallet.account))
                .join_from(receiver_account, receiver_user, JOIN.LEFT_OUTER, attr='receiver_user', on=(receiver_account.record_id == receiver_user.id))
                .join_from(receiver_account, receiver_station, JOIN.LEFT_OUTER, attr='receiver_station', on=(receiver_account.record_id == receiver_station.id))
                .where(reduce(operator.or_, where_clauses))
                .order_by(Payments.modified_on.desc())
                .offset(offset).limit(limit))

    def fetch_payments_by_id(self, payment_id):
        sender_account = Accounts.alias()
        sender_wallet = Wallets.alias()
        sender_user = Users.alias()
        receiver_account = Accounts.alias()
        receiver_wallet = Wallets.alias()
        receiver_user = Users.alias()

        return (Payments.select(Payments.id, Payments.payment_status, Payments.modified_on, Payments.comment, Payments.order_amount,
                                Orders.order_id, Orders.order_status, Orders.order_type, Invoices.id,
                                sender_account.record_id, sender_account.alias_name, sender_wallet.record_id, sender_wallet.name,
                                sender_user.record_id, sender_user.customer_id, sender_user.phone_number, sender_user.name, sender_user.verified,
                                receiver_account.record_id, receiver_account.alias_name, receiver_wallet.record_id, receiver_wallet.name,
                                receiver_user.record_id, receiver_user.customer_id, receiver_user.phone_number, receiver_user.name, receiver_user.verified
                                )
                .join_from(Payments, Orders, attr='order', on=((Payments.order == Orders.order_id) &
                                                               ((Orders.order_type == OrderTypes.PurchaseToken) | (Orders.order_type == OrderTypes.PayForBooking) |(Orders.order_type == OrderTypes.EncashToken) |
                                                               ((Orders.order_type == OrderTypes.PayForToken) & ((Orders.order_status == 'FAILURE') | (Orders.order_status == 'CANCELLED'))))))
                .join_from(Payments, Invoices, attr='invoices', on=(Invoices.payment == Payments.id))
                .join_from(Payments, sender_account, attr='sender_account', on=(Payments.sender == sender_account.record_id))
                .join_from(sender_account, sender_wallet, attr='sender_wallet', on=(sender_account.record_id == sender_wallet.account))
                .join_from(sender_account, sender_user, JOIN.LEFT_OUTER, attr='sender_user', on=(sender_account.record_id == sender_user.id))
                .join_from(Payments, receiver_account, attr='receiver_account', on=(Payments.receiver == receiver_account.record_id))
                .join_from(receiver_account, receiver_wallet, attr='receiver_wallet', on=(receiver_account.record_id == receiver_wallet.account))
                .join_from(receiver_account, receiver_user, JOIN.LEFT_OUTER, attr='receiver_user', on=(receiver_account.record_id == receiver_user.id))
                .where(Payments.id == payment_id).get())


