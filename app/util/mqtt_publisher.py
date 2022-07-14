#!/usr/bin/env python3
import json

import paho.mqtt.client as mqtt

from app import config
from app.config import TOPIC

# This is the Publisher
from app.log import LOG
from app.util.datetime_util import datetime_now
from app.util.json_util import UUIDEncoder


def __send_message_to_topic__(topic_name, message, broker_url, port):
    client = mqtt.Client()
    client.username_pw_set(username=TOPIC['username'], password=TOPIC['password'])
    client.connect(broker_url, port, 60)
    client.publish(topic_name, message, qos=2)
    client.disconnect()


def __sms_content_dict__(application_name, mobile_no, otp, txn_id):
    return {
        "meta": application_name,
        "phoneNumber": mobile_no,
        "content": {
            "otp": otp,
        },
        "txnId": txn_id
    }


def send_sms(topic_name, application_name, mobile_no, otp, txn_id):
    message = to_json(__sms_content_dict__(application_name, mobile_no, otp, txn_id))
    __send_message_to_topic__(topic_name, message, TOPIC['broker_url'], int(TOPIC['port']))


def to_json(json_dict):
    return json.dumps(json_dict, cls=UUIDEncoder)


def __notification_content_dict__(application_name, notification):
    notification['meta'] = application_name
    return notification


def send_notification(topic_name, application_name, notification):
    message = to_json(__notification_content_dict__(application_name, notification))
    LOG.info('message %s' % message)
    LOG.info(topic_name)
    __send_message_to_topic__(topic_name, message, TOPIC['broker_url'], int(TOPIC['port']))


def __booking_content_dict__(application_name, booking):
    return {
        "meta": application_name,
        "resourceType": "BOOKING",
        "resource": booking,
        "publishedOn": datetime_now()
    }

def __booking_content_dict_for_temp__(application_name, booking):
    booking["meta"] = application_name
    return booking


def send_booking_details(topic_name, application_name, booking):
    message = to_json(__booking_content_dict__(application_name, booking))
    __send_message_to_topic__(topic_name, message, config.TOPIC['broker_url'], int(config.TOPIC['port']))


def send_booking_details_for_temp(topic_name, application_name, booking):
    message = to_json(__booking_content_dict_for_temp__(application_name, booking))
    __send_message_to_topic__(topic_name, message, config.TOPIC['broker_url'], int(config.TOPIC['port']))
