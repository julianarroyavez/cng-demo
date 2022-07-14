from peewee import fn

from app.domain.notification_schema import Notifications


class NotificationRepository:

    def insert(self, notification, user_id, mobile_id):
        return (Notifications
                .create(id=fn.nextval('notifications_id_seq'),
                        created_by=user_id,
                        modified_by=user_id,
                        event=notification.event,
                        event_time=notification.event_time,
                        recipient=user_id,
                        recipient_device=mobile_id,
                        engaged_action=notification.engaged_action,
                        engaged_source=notification.engaged_source,
                        linked_resource=notification.linked_resource,
                        generated_on=notification.generated_on,
                        data=notification.data))

    def fetch_all_by_user(self, columns, user_id, offset, limit, after, type_configs):
        return (Notifications
                .select(*columns)
                .where(((Notifications.recipient == str(user_id)) &
                        (Notifications.event_time >= after)) &
                       (Notifications.event.in_(type_configs)))
                .order_by(Notifications.event_time.desc())
                .offset(offset)
                .limit(limit))

    def fetch_by_id(self, notification_id):
        return Notifications.get_by_id(notification_id)

    def update_notification_json_object(self, notification_id, data):
        (Notifications
         .update(data=data)
         .where(Notifications.id == notification_id)
         .execute())

    def delete_notifications(self, resource_id, events):
        (Notifications
         .delete()
         .where(Notifications.linked_resource.contains({'resource_id': str(resource_id)}) &
                (Notifications.event.in_(events)))
         .execute())

    def update_notification(self, notification, now):
        (Notifications
         .update({
            Notifications.received_on: notification['received_on'],
            Notifications.displayed_on: notification['displayed_on'],
            Notifications.engaged_on: notification['engaged_on'],
            Notifications.engaged_action: notification['engaged_action'],
            Notifications.engaged_source: notification['engaged_source'],
            Notifications.modified_on: now
         })
         .where(Notifications.id == notification['id'])
         .execute())

    def update_notification_cancelled_time(self, resource_id, now, events):
        (Notifications
         .update(cancelled_on=now)
         .where(Notifications.linked_resource.contains({'resource_id': str(resource_id)}) &
                (Notifications.event.in_(events)))
         .execute())

    def update_record(self, record):
        return record.save()

