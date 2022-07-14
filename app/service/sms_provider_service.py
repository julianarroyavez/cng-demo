# GET https://2factor.in/API/V1/{api_key}/SMS/{phone_number}/{otp}
# GET https://2factor.in/API/V1/{api_key}/SMS/{phone_number}/{otp}/{template_name} --optional //Hygge EV
import requests

from app import config

__SmsProviderServer = config.SMS['sms_provider_server']
__ApiKey = config.SMS['api_key']
__OtpSmsTemplateName = config.SMS['otp_sms_template_name']


# todo move this entire file to new project will be used by listener + do not use this method too much on dev testing
#  sms costing is enable
def send_otp_sms(phone_number, otp):
    api_endpoint = '{provider_url}/{api_key}/SMS/{phone_number}/{otp}/{template_name}'.format(**dict(
        provider_url=__SmsProviderServer,
        api_key=__ApiKey,
        phone_number=phone_number,
        otp=otp,
        template_name=__OtpSmsTemplateName
    ))
    response = requests.get(api_endpoint)
    return {
        "status_code": response.status_code,
        "response_body": response.json()
    }

