import operator
from functools import reduce

from app.domain.auth_schema import AppConfigs, Visibility
from app.log import LOG


class AppConfigRepository:
    def fetch_all_after_time(self, value_from, now):
        return AppConfigs.select().where(
            (AppConfigs.validity_start <= now)
            & (AppConfigs.validity_end > now)
            & (AppConfigs.validity_start >= value_from)
        )

    def fetch_by_keys(self, where_clauses, now):
        return (AppConfigs
                .select()
                .where(reduce(operator.or_, where_clauses)
                       & (AppConfigs.validity_start <= now)
                       & (AppConfigs.validity_end > now)))

    def fetch_value_by_key(self, key, now):
        return (AppConfigs
                .select()
                .where((AppConfigs.key == key)
                       & (AppConfigs.validity_start <= now)
                       & (AppConfigs.validity_end > now)).get().value)

    def fetch_max_nozzle_guns_in_one_charger(self, now):
        return int(AppConfigs
                   .select()
                   .where((AppConfigs.key == 'max_nozzle_guns_in_one_charger')
                          & (AppConfigs.validity_start <= now)
                          & (AppConfigs.validity_end > now))
                   .get()
                   .value)

    def fetch_key_containing_value(self, value_substring):
        return (AppConfigs
                .select(AppConfigs.key)
                .where(AppConfigs.value.contains(value_substring)))

    def fetch_notification_bar_events(self, now):
        return (AppConfigs
                .select()
                .where((AppConfigs.key == 'NOTIFICATION_BAR')
                       & (AppConfigs.validity_start <= now)
                       & (AppConfigs.validity_end > now)).get().value)

    def fetch_notification_bell_icon_events(self, now):
        return (AppConfigs
                .select()
                .where((AppConfigs.key == 'NOTIFICATION_BELL_ICON')
                       & (AppConfigs.validity_start <= now)
                       & (AppConfigs.validity_end > now)).get().value)

    def fetch_all_notification_events(self, now):
        return (AppConfigs
                .select()
                .where((AppConfigs.key == 'NOTIFICATION_ALL')
                       & (AppConfigs.validity_start <= now)
                       & (AppConfigs.validity_end > now)).get().value)

    def fetch_all_notification_events_for_deep_link(self, now):
        return (AppConfigs
                .select()
                .where((AppConfigs.key == 'NOTIFICATION_DEEP_LINK')
                       & (AppConfigs.validity_start <= now)
                       & (AppConfigs.validity_end > now)).get().value)

    def fetch_all_notification_scheduled_events(self, now):
        return (AppConfigs
                .select()
                .where((AppConfigs.key == 'NOTIFICATION_SCHEDULED')
                       & (AppConfigs.validity_start <= now)
                       & (AppConfigs.validity_end > now)).get().value)

    def fetch_all__visibility_public_after_time(self, value_from, now):
        return AppConfigs.select().where(
            (AppConfigs.validity_start <= now)
            & (AppConfigs.validity_end > now)
            & (AppConfigs.validity_start >= value_from)
            & (AppConfigs.visibility == Visibility.PUBLIC)
        )

    def fetch_all_slot_durations(self, now):
        return (AppConfigs
                .select()
                .where((AppConfigs.key == 'slot_durations')
                       & (AppConfigs.validity_start <= now)
                       & (AppConfigs.validity_end > now)).get().value)

    def fetch_slot_break(self, now):
        return (AppConfigs
                .select()
                .where((AppConfigs.key == 'slot_break_in_mins')
                       & (AppConfigs.validity_start <= now)
                       & (AppConfigs.validity_end > now)).get())

    def fetch_hygge_box_simulation(self, now):
        return (AppConfigs
                .select()
                .where((AppConfigs.key == 'hygge_box_simulator')
                       & (AppConfigs.validity_start <= now)
                       & (AppConfigs.validity_end > now)).get())
