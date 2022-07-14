import os
import configparser

BRAND_NAME = "Hygge EV API"

APP_ENV = os.environ.get("APP_ENV") or "local"  # or 'prod' to load production & 'qa' to load QA
print('Configuring app with env: {}'.format(APP_ENV))
INI_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "../conf/application/{}.ini".format(APP_ENV)
)

CONFIG = configparser.ConfigParser()
CONFIG.read(INI_FILE)
POSTGRES = CONFIG["postgres"]
if APP_ENV != "local":
    DB_CONFIG = (POSTGRES["host"], POSTGRES["database"])
    DATABASE_URL = "postgresql+psycopg2://%s/%s" % DB_CONFIG
else:
    DB_CONFIG = (
        POSTGRES["user"],
        POSTGRES["password"],
        POSTGRES["host"],
        POSTGRES["database"],
        POSTGRES["options"]
    )
    DATABASE_URL = "postgresql+psycopg2://%s:%s@%s/%s?options=%s" % DB_CONFIG

LOG_LEVEL = CONFIG["logging"]["level"]
LOG_DIRECTORY = CONFIG["logging"]["log_directory"]
DB_LOG_LEVEL = CONFIG["logging"]["db_level"]

TOPIC = CONFIG['topic']

DEEP_LINK = CONFIG["deepLink"]

TIMEZONE = CONFIG["timezone"]

SUPPORT = CONFIG["support"]

OTP = CONFIG["otp"]

PAYTM = CONFIG["paytm"]

DURATION = CONFIG["duration"]

SMS = CONFIG["sms"]

SESSION = CONFIG["session"]

SIMULATOR = CONFIG["simulator"]

NAVIGATION = CONFIG["navigation"]
