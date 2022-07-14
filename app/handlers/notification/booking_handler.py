import datetime

from pytz import timezone

from app import config
from app.domain.notification_schema import NotificationEvent, Action, Notifications
from app.log import LOG
from app.util.datetime_util import datetime_now, get_time_difference_using_minutes, get_time_difference_using_hours, \
    date_and_time_to_datetime, time_utc_to_ist
from app.util.notification_util import NotificationUtil


class BookingHandler:

    def create_booking_notification(self, booking, user_id, device):
        notifications = []
        booking_confirmation = self.create_booking_confirmation_notification(booking_data=booking,
                                                                             user_id=user_id,
                                                                             device_id=device.id)
        notifications.append(booking_confirmation)
        booking_reminders = self.create_booking_reminder_notification(booking_data=booking,
                                                                      user_id=user_id,
                                                                      device_id=device.id)
        for notification in booking_reminders:
            notifications.append(notification)

        send_notification = {
            "notifications": notifications,
            "to_device": device.fcm_token
        }
        return send_notification

    def create_booking_cancellation_notification(self, booking_data, user_id, device, booking_station_name):
        notification_util = NotificationUtil()
        notifications = []
        events = [NotificationEvent.BookingReminderFirst, NotificationEvent.BookingReminderSecond]
        notification = Notifications()
        notification.event = NotificationEvent.BookingCancellation
        notification.event_time = datetime.datetime.now(timezone('UTC'))
        replaceable_value = [booking_station_name]
        title_obj = NotificationEvent.get_title_and_message_for_booking(
            string=NotificationEvent.BookingCancellation.value,
            replaceable_value=replaceable_value)
        notification.engaged_source = 'notification'
        notification.engaged_action = Action.Click.value
        notification.recipient = user_id
        notification.recipient_device = device.id
        notification.linked_resource = {"resource_id": str(booking_data), "resource": "Booking"}
        notification.generated_on = datetime_now()
        notification.data = notification_util.create_single_notification_json_data(notification=notification,
                                                                                   title_obj=title_obj)
        notifications.append(notification)

        send_notification = {
            "notifications": notifications,
            "to_device": device.fcm_token,
            "booking_id": booking_data,
            "events": events
        }

        return send_notification

    def create_booking_rejection_notification(self, booking_data, user_id, device):
        notification_util = NotificationUtil()
        notifications = []
        events = [NotificationEvent.BookingReminderFirst, NotificationEvent.BookingReminderSecond]
        notification = Notifications()
        notification.event = NotificationEvent.BookingRejection
        notification.event_time = datetime.datetime.now(timezone('UTC'))
        replaceable_value = [str(booking_data.stations.name)]
        title_obj = NotificationEvent.get_title_and_message_for_booking(string=NotificationEvent.BookingRejection.value,
                                                                        replaceable_value=replaceable_value)
        notification.engaged_source = 'notification'
        notification.engaged_action = Action.Click.value
        notification.recipient = user_id
        notification.recipient_device = device.id
        notification.linked_resource = {"resource_id": str(booking_data.id), "resource": "Booking"}
        notification.generated_on = datetime_now()
        notification.data = notification_util.create_single_notification_json_data(notification=notification,
                                                                                   title_obj=title_obj)
        notifications.append(notification)

        send_notification = {
            "notifications": notifications,
            "to_device": device.fcm_token,
            "booking_id": booking_data.id,
            "events": events
        }

        return send_notification

    def create_booking_confirmation_notification(self, booking_data, user_id, device_id):
        notification_util = NotificationUtil()

        station = booking_data['station']
        booking = booking_data['booking']

        notification = Notifications()
        notification.event = NotificationEvent.BookingConfirmation
        notification.event_time = booking.created_on
        replaceable_value = [station.name]

        title_obj = NotificationEvent.get_title_and_message_for_booking(
            string=NotificationEvent.BookingConfirmation.value,
            replaceable_value=replaceable_value)
        notification.engaged_source = 'notification'
        notification.engaged_action = Action.Click.value
        notification.recipient = user_id
        notification.recipient_device = device_id

        notification.linked_resource = {"resource_id": str(booking.booking_id), "resource": "Booking"}

        notification.generated_on = datetime_now()

        notification.data = notification_util.create_single_notification_json_data(notification=notification,
                                                                                   title_obj=title_obj)
        return notification

    def create_booking_reminder_notification(self, booking_data, user_id, device_id):
        notification_util = NotificationUtil()
        station = booking_data['station']
        booking = booking_data['booking']
        notifications = []
        date_value = date_and_time_to_datetime(date_value=booking.service_date,
                                               time_value=booking.slot.start_time,
                                               date_format='%Y-%m-%d %H:%M:%S')

        time = time_utc_to_ist(date_val=date_value, hours=5, mins=30)

        reminder_count = self.__get_reminder_notification_count(event_date=date_value)
        replaceable_value = [time, station.name]
        for x in range(reminder_count):
            notification = Notifications()
            if x == 0:
                notification.event = NotificationEvent.BookingReminderSecond
                notification.event_time = get_time_difference_using_minutes(date_value, 15)
                LOG.info('notification event time: %s ' % notification.event_time)
                title_obj = NotificationEvent.get_title_and_message_for_booking(
                    string=NotificationEvent.BookingReminderSecond.value
                    , replaceable_value=replaceable_value)

            elif x == 1:
                notification.event = NotificationEvent.BookingReminderFirst
                notification.event_time = get_time_difference_using_hours(date_value, 2)
                title_obj = NotificationEvent.get_title_and_message_for_booking(
                    string=NotificationEvent.BookingReminderFirst.value,
                    replaceable_value=replaceable_value)

            notification.engaged_source = 'notification'
            notification.engaged_action = Action.Click.value
            notification.recipient = user_id
            notification.recipient_device = device_id
            notification.linked_resource = {"resource_id": str(booking.booking_id), "resource": "Booking"}
            notification.generated_on = datetime_now()
            notification.data = notification_util.create_single_notification_json_data(notification=notification,
                                                                                       title_obj=title_obj)
            notifications.append(notification)
        return notifications

    def __get_reminder_notification_count(self, event_date):
        count = 0
        now = datetime.datetime.utcnow()

        duration = event_date - now

        total_seconds = duration.total_seconds()

        if total_seconds >= 60 * 15:
            count = count + 1

        if total_seconds >= 60 * 120:
            count = count + 1

        return count
