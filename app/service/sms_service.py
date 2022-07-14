from app.domain.auth_schema import AuthAttempts
from app import config
from app import log
from app.service.sms_provider_service import send_otp_sms
from app.util.datetime_util import datetime_now
from app.util.mqtt_publisher import send_sms

LOG = log.get_logger()


class SmsService:

    # todo uncomment push to queue code and let message go to queue for otp
    def send_otp_sms(self, phone_number, otp, txn_id):
        try:
            if phone_number != config.SMS['default_number']:
                topic_name = config.TOPIC['sms_otp_topic']
                application_name = config.TOPIC['application_name']
                send_sms(topic_name=topic_name, application_name=application_name, mobile_no=phone_number, otp=otp, txn_id=txn_id)
        except Exception as e:
            LOG.error("Failed to push sms message in queue")
            LOG.error(e)

    # todo move this method logic to another project's listener method + copy dependent files too to new project
    def send_direct_sms(self, phone_number, otp, txn_id):
        response = send_otp_sms(phone_number, otp)
        LOG.info('OTP SMS sent to %s' % phone_number)
        attempt = AuthAttempts.get(AuthAttempts.txn_id == txn_id)
        attempt.modified_on = datetime_now()
        attempt.gateway_send_otp_res_status = response['status_code']
        attempt.gateway_send_otp_res_body = response['response_body']
        attempt.save()
