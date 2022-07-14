import stomp

from app.util.json_util import to_json


def __send_message_to_queue__(queue_name, message):
    conn = stomp.Connection10()
    conn.connect()
    conn.send(destination=queue_name, body=message)
    #conn.disconnect() # cross check and uncomment


def __sms_content_dict__(application_name, mobile_no, otp):
    return {
        "meta": application_name,
        "mobileNumber": mobile_no,
        "content": {
            "otp": otp,
        },
    }


def send_sms(queue_name, application_name, mobile_no, otp):
    message = to_json(__sms_content_dict__(application_name, mobile_no, otp))
    __send_message_to_queue__(queue_name, message)
