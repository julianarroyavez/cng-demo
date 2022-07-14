import requests
import json
from paytmchecksum import PaytmChecksum

from app import config
from app.log import PAYTM_LOG

# hygge paytm keys
MERCHANT_KEY = config.PAYTM['merchant_key']
MERCHANT_ID = config.PAYTM['merchant_id']
content_type = config.PAYTM['content_type']
payment_mode = config.PAYTM['payment_mode']


class PaytmService:
    def initiate_txn(self, order):
        paytm_params = dict()
        PAYTM_LOG.info(type(config.PAYTM['callback_url']))
        paytm_params["body"] = {"requestType": "Payment", "mid": MERCHANT_ID, "websiteName": "WEBSTAGING",
                               "orderId": order.order_id, "mode": payment_mode, "channels": ["UPIPUSH"],
                               "callbackUrl": (config.PAYTM['callback_url'] % order.order_id),
                               "txnAmount": {"value": float(order.total), "currency": config.PAYTM['currency']},
                               "userInfo": {"custId": config.PAYTM['customer_id']}
                               }

        checksum = PaytmChecksum.generateSignature(json.dumps(paytm_params["body"]), MERCHANT_KEY)
        paytm_params["head"] = {"signature": checksum}
        post_data = json.dumps(paytm_params)

        url = config.PAYTM['transaction_url'] % (MERCHANT_ID, order.order_id)
        response = requests.post(url, data=post_data, headers={"Content-type": content_type}).json()
        PAYTM_LOG.info('INIT Paytm Gateway Response %s' % response)

        return response

    def verify_txn(self, unique_order_id):
        paytm_params = dict()
        paytm_params["body"] = {
            "mid": MERCHANT_ID,
            "orderId": unique_order_id,
        }

        checksum = PaytmChecksum.generateSignature(json.dumps(paytm_params["body"]), MERCHANT_KEY)
        paytm_params["head"] = {"signature": checksum}
        post_data = json.dumps(paytm_params)

        url = config.PAYTM['status_url']
        payment_status_response = requests.post(url, data=post_data,
                                                headers={"Content-type": content_type}).json()
        PAYTM_LOG.info('Verify TXN Paytm Gateway response: %s' % payment_status_response)

        return payment_status_response

    def cancel_txn(self, order_id):
        PAYTM_LOG.info('Cancel Txn of ID %s' % order_id)
        paytm_params = dict()
        paytm_params["paytmOrderIds"] = [order_id]
        post_data = json.dumps(paytm_params)

        checksum = PaytmChecksum.generateSignature(post_data, MERCHANT_KEY)
        x_checksum = checksum
        x_mid = MERCHANT_ID

        # for Staging
        url = config.PAYTM['staging_url']

        # for Production
        # url = "https://dashboard.paytm.com/bpay/api/v1/disburse/order/cancel"

        response = requests.post(url, data=post_data, headers={"Content-type": content_type, "x-mid": x_mid,
                                                               "x-checksum": x_checksum}).json()

        PAYTM_LOG.info('Cancel Txn Paytm Gateway response %s' % response)
        return response
