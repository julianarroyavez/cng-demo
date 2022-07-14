import math
import random
import secrets
import string

digits = '0123456789'


def generate_key(key_length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=key_length))


def generate_otp():
    otp = ''
    for _ in range(6):
        otp += str(secrets.randbelow(8) + 1)
    return otp


def check_if_alphanumeric(value: str):
    return value.isalnum()
