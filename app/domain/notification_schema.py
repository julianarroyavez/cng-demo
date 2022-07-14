import enum

from peewee import BigAutoField, DateTimeField, ForeignKeyField, CharField
from playhouse.postgres_ext import HStoreField, BinaryJSONField

from app.constant import schema_constant
from app.domain.auth_schema import Users, MobileDevices
from app.domain.base import BaseModel, EnumField
from app.errors import InvalidParameterError, FieldErrors, InvalidFieldError

invalid_notification_event = 'Invalid Notification Event'


class NotificationEvent(enum.Enum):
    TxnTransferToken = 'TXN_TRANSFER_TOKEN'
    TxnTransferFailedToken = 'TXN_TRANSFER_TOKEN_FAILED'
    BookingConfirmation = 'BOOKING_CONFIRMATION'
    BookingReminderFirst = 'BOOKING_REMINDER_FIRST'
    BookingReminderSecond = 'BOOKING_REMINDER_SECOND'
    BookingCancellation = 'BOOKING_CANCELLATION'
    BookingRejection = 'BOOKING_REJECTION'
    VehicleAddition = 'VEHICLE_ADDITION'
    VehicleVerification = 'VEHICLE_VERIFICATION'
    UserVerification = 'USER_VERIFICATION'
    UserLogin = 'USER_LOGIN'
    BookingRating = 'BOOKING_RATING'
    TxnAddToken = 'TXN_ADDITION_TOKEN'
    StationRating = 'STATION_RATING'

    @staticmethod
    def from_str(string):
        if string == 'TXN_TRANSFER_TOKEN':
            return NotificationEvent.TxnTransferToken
        if string == 'TXN_TRANSFER_TOKEN_FAILED':
            return NotificationEvent.TxnTransferFailedToken
        if string == 'BOOKING_CONFIRMATION':
            return NotificationEvent.BookingConfirmation
        if string == 'BOOKING_REMINDER_FIRST':
            return NotificationEvent.BookingReminderFirst
        if string == 'BOOKING_REMINDER_SECOND':
            return NotificationEvent.BookingReminderSecond
        if string == 'BOOKING_CANCELLATION':
            return NotificationEvent.BookingCancellation
        if string == 'BOOKING_REJECTION':
            return NotificationEvent.BookingRejection
        if string == 'VEHICLE_ADDITION':
            return NotificationEvent.VehicleAddition
        if string == 'VEHICLE_VERIFICATION':
            return NotificationEvent.VehicleVerification
        if string == 'USER_VERIFICATION':
            return NotificationEvent.UserVerification
        if string == 'USER_LOGIN':
            return NotificationEvent.UserLogin
        if string == 'BOOKING_RATING':
            return NotificationEvent.BookingRating
        if string == 'TXN_ADDITION_TOKEN':
            return NotificationEvent.TxnAddToken
        if string == 'STATION_RATING':
            return NotificationEvent.StationRating
        else:
            raise InvalidParameterError(description=invalid_notification_event,
                                        field_errors=[InvalidFieldError(FieldErrors.Notification)])

    @staticmethod
    def get_title_and_message_for_payment(string, replaceable_value):

        if string == 'TXN_TRANSFER_TOKEN':
            message = ("%s tokens have been received from +91 %s." % (replaceable_value[0], replaceable_value[1]))
            return {"title": "Tokens Received", "message": message}

        elif string == 'TXN_ADDITION_TOKEN':
            message = ("%s tokens have been added to your wallet successfully" % replaceable_value[0])
            return {"title": "Tokens Received", "message": message}

        elif string == 'TXN_TRANSFER_TOKEN_FAILED':
            return {"title": "Add token failed", "message": "Add token failed. Please try again later"}

        else:
            raise InvalidParameterError(description=invalid_notification_event,
                                        field_errors=[InvalidFieldError(FieldErrors.Notification)])

    @staticmethod
    def get_title_and_message_for_booking(string, replaceable_value):

        if string == 'BOOKING_CONFIRMATION':
            message = f"Your booking has been confirmed at {replaceable_value[0]} station"
            return {"title": "Booking Confirmed", "message": message}

        elif string == 'BOOKING_REMINDER_FIRST' or string == 'BOOKING_REMINDER_SECOND':
            message = f"Reminder for upcoming booking on {replaceable_value[0]} at {replaceable_value[1]} " \
                      f"station.Click to navigate"
            return {"title": "Upcoming Booking", "message": message}

        elif string == 'BOOKING_CANCELLATION':
            message = f"Your booking for {replaceable_value[0]} station has been canceled."
            return {"title": "Booking Canceled", "message": message}

        elif string == 'BOOKING_REJECTION':
            message = ("Booking at %s canceled due to operational reasons . The tokens will be credited back"
                       % replaceable_value[0])
            return {"title": "Booking Canceled", "message": message}

        else:
            raise InvalidParameterError(description=invalid_notification_event,
                                        field_errors=[InvalidFieldError(FieldErrors.Notification)])

    @staticmethod
    def get_title_and_message_for_user(string, replaceable_value):

        if string == 'VEHICLE_ADDITION':
            return {"title": "Vehicle Addition", "message": "A new vehicle has been added successfully to your account"}

        elif string == 'VEHICLE_VERIFICATION':
            if replaceable_value[0] == 'VERIFIED':
                return {"title": "Vehicle Verification", "message": "Your vehicle has been verified ."}
            else:
                return {"title": "Vehicle Verification", "message": "Your vehicle verification has been rejected for "
                                                                    "some reason."}

        elif string == 'USER_VERIFICATION':
            if replaceable_value[0] == 'VERIFIED':
                return {"title": "User Verification", "message": "Your profile has been verified . "
                                                                 "Search for the stations to book slot"}
            else:
                return {"title": "User Verification", "message": "Your profile verification has been rejected for "
                                                                 "some reason."}

        elif string == 'USER_LOGIN':
            message = ("New login into account on %s" % replaceable_value[0])
            return {"title": "Login", "message": message}

        elif string == 'BOOKING_RATING':
            return {"title": "", "message": ""}

        else:
            raise InvalidParameterError(description=invalid_notification_event,
                                        field_errors=[InvalidFieldError(FieldErrors.Notification)])


class Action(enum.Enum):
    Click = 'CLICK'
    PrimaryButton = 'PRIMARY_BUTTON'
    PopupScreen = 'POPUP_SCREEN'
    # TODO add other action enum once confirmed by Aishwarya.


class NotificationType(enum.Enum):
    BellIcon = 'NOTIFICATION_BELL_ICON'
    NotificationBar = 'NOTIFICATION_BAR'
    BothBellAndBar = 'NOTIFICATION_BELL_AND_BAR'
    Popup = 'POPUP'


class Notifications(BaseModel):
    id = BigAutoField()
    event = EnumField(enum_class=NotificationEvent)
    event_time = DateTimeField(null=True)
    data = BinaryJSONField(null=True)
    recipient = ForeignKeyField(Users, column_name='user_record_id', lazy_load=False)
    recipient_device = ForeignKeyField(MobileDevices, column_name='mobile_record_id', lazy_load=False, null=True)
    linked_resource = HStoreField(null=True)
    generated_on = DateTimeField(null=True)
    sent_on = DateTimeField(null=True)
    received_on = DateTimeField(null=True)
    displayed_on = DateTimeField(null=True)
    engaged_on = DateTimeField(null=True)
    cancelled_on = DateTimeField(null=True)
    engaged_action = CharField(null=True)
    engaged_source = CharField(null=True)

    class Meta:
        schema = schema_constant.engagement
