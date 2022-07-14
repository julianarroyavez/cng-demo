from app.domain.payment_schema import Wallets
from app.log import LOG
from app.util.datetime_util import datetime_now


class WalletsRepository:

    def insert(self, primary_key, record_id, name, account_id, creator_user_id, now):
        return (Wallets
                .create(id=primary_key,
                        record_id=record_id,
                        account=account_id,
                        name=name,
                        created_on=now,
                        modified_on=now,
                        validity_start=now,
                        created_by=creator_user_id,
                        modified_by=creator_user_id))

    def fetch_by_account_id(self, account_id, now):
        return (Wallets
                .select(Wallets.id, Wallets.name, Wallets.balance)
                .where((Wallets.account == account_id)
                       & (Wallets.validity_start <= now)
                       & (Wallets.validity_end > now))
                .get())

    def fetch_by_name(self, name, now):
        return (Wallets
                .select(Wallets.balance, Wallets.id)
                .where((Wallets.name == name)
                       & (Wallets.validity_start <= now)
                       & (Wallets.validity_end > now))
                .get())

    def fetch_hygge_mart_wallet(self):
        return self.fetch_by_name('hygge-mart', now=datetime_now())

    def fetch_hygge_booking_bucket_wallet(self):
        return self.fetch_by_name('hygge-booking-bucket', now=datetime_now())

    def update(self, record):
        return record.save()

    def update_balance(self, record, new_balance):
        record.balance = new_balance
        self.update(record)

    def update_transit_balance(self, record, new_balance, new_transit_balance):
        record.balance = new_balance
        record.in_transit = new_transit_balance
        self.update(record)
