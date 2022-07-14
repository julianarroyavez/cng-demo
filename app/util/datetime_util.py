import datetime

from pytz import timezone
from dateutil.relativedelta import relativedelta

from app import config
from app.log import LOG

ist_timezone = config.TIMEZONE['timezone']
date_format_in_yyyy_mm_dd = '%Y-%m-%d'
date_format_in_yyyy_mm_dd_hh_mm_ss_z = '%Y-%m-%dT%H:%M:%SZ'
time_format_in_hh_mm_ss = "%H:%M:%S"
date_format_in_i_m_p = '%I:%M%p'
date_format_in_yyyy_mm_dd_hh_mm_ss = '%Y-%m-%dT%H:%M:%S'
date_format_in_dd_mm = '%d %b'
date_format_in_yyyy = '%Y'


def datetime_now():
    return datetime.datetime.utcnow().isoformat()


def current_time_millis():
    return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)


def before_now(minutes):
    return datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)


def after_now(minutes):
    return datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)


def after_now(hours):
    return datetime.datetime.utcnow() + datetime.timedelta(hours=hours)


def to_date(date_in_str):
    return datetime.datetime.strptime(date_in_str, date_format_in_yyyy_mm_dd).date()


def to_time(time_in_str):
    return datetime.datetime.strptime(time_in_str, '%H:%M:%S').time()


def time_to_mins(time):
    return int((time.hour * 60) + time.minute)


def min_to_time(mins):
    return datetime.time(hour=int(mins / 60), minute=int(mins % 60))


def to_12_hour_format_with_meridian(time):
    time = time.strftime(time_format_in_hh_mm_ss)
    d = datetime.datetime.strptime(time, time_format_in_hh_mm_ss)
    return d.strftime("%I:%M %p")


def to_12_hour_format_without_meridian(time):
    time = time.strftime(time_format_in_hh_mm_ss)
    d = datetime.datetime.strptime(time, time_format_in_hh_mm_ss)
    return d.strftime("%I:%M")


def get_rem_time_from_now(timestamp):
    result = timestamp - datetime.datetime.utcnow()
    return result


def get_time_delta_in_minutes(timedelta):
    return timedelta.total_seconds() / 60


def before_given_time(timestamp, minutes):
    return timestamp - datetime.timedelta(minutes=minutes)


def to_day_of_week_in_binary(date):
    return '{0:07b}'.format(pow(2, to_date(date).weekday()))


def get_minimum_date_value():
    return datetime.datetime(1960, 1, 1)


def get_time_difference_using_hours(date, hours):
    final_time = date - relativedelta(hours=hours)
    return final_time.astimezone(timezone(ist_timezone))


def get_time_difference_using_minutes(date, minutes):
    final_time = date - relativedelta(minutes=minutes)
    return final_time.astimezone(timezone(ist_timezone))


def date_format(date_val):
    return date_val.strftime(date_format_in_yyyy_mm_dd_hh_mm_ss_z)


def date_to_ist_format(date_val):
    try:
        return date_val.strftime('%a %-d %b, %Y at %I:%M%p')
    except:
        return date_val.strftime('%a %d %b, %Y at %I:%M%p')

def date_to_time_ist_format(date_val):
    return date_val.strftime(date_format_in_i_m_p).now(timezone(ist_timezone))


def date_and_time_to_datetime(date_value, time_value):
    date_time_str = '%s %s' % (str(date_value), time_value)
    return datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')


def time_utc_to_ist(date_val, hours, mins):
    time_change = datetime.timedelta(hours=hours, minutes=mins)
    new_time = date_val + time_change
    return new_time.strftime(date_format_in_i_m_p)


def get_previous_date(date):
    date = datetime.datetime.strptime(date, date_format_in_yyyy_mm_dd)
    result = date - relativedelta(hours=24)
    return result.strftime(date_format_in_yyyy_mm_dd)


def get_minimum_date_value():
    return datetime.datetime(1960, 1, 1)


def date_format(date_val):
    return date_val.strftime(date_format_in_yyyy_mm_dd_hh_mm_ss_z)


def date_and_time_to_datetime(date_value, time_value, date_format):
    date_time_str = '%s %s' % (str(date_value), time_value)
    return datetime.datetime.strptime(date_time_str, date_format)


def time_utc_to_ist(date_val, hours, mins):
    time_change = datetime.timedelta(hours=hours, minutes=mins)
    new_time = date_val + time_change
    return new_time.strftime(date_format_in_i_m_p)


def get_previous_date(date):
    date = datetime.datetime.strptime(date, date_format_in_yyyy_mm_dd)
    result = date - relativedelta(hours=24)
    return result.strftime(date_format_in_yyyy_mm_dd)


def get_date_from_string(date) -> datetime.datetime:
    return datetime.datetime.strptime(date, date_format_in_yyyy_mm_dd)


def get_previous_date_in_string(date) -> str:
    try:
        return date.strftime(date_format_in_yyyy_mm_dd)
    except Exception:
        return date


def convert_date_to_duration_today(date) -> str:
    return date.strftime('%d %B %Y')


def convert_date_to_duration_month(date) -> str:
    return date.strftime('%B %Y')


def get_month_start_date(date) -> datetime.datetime:
    date = get_date_from_string(date=date)
    return date.replace(day=1).strftime(date_format_in_yyyy_mm_dd)


def get_month_last_date(date) -> datetime.datetime:
    date = get_date_from_string(date=date)
    date = date.replace(day=28) + datetime.timedelta(days=4)
    return date - datetime.timedelta(days=date.day)


def convert_date_to_text_format(date) -> str:
    return datetime.datetime.strptime(date, date_format_in_yyyy_mm_dd).strftime('%d %B %Y')


def get_date_time_from_string(date) -> datetime.datetime:
    return datetime.datetime.strptime(date, date_format_in_yyyy_mm_dd_hh_mm_ss_z)


def get_date_in_string_format(date) -> str:
    return date.strftime(date_format_in_yyyy_mm_dd)


def date_from_datetime_now():
    return datetime.datetime.now().date().isoformat()


def add_date_with_min_time(date) -> str:
    return '%sT00:00:00Z' % date


def add_date_with_max_time(date) -> str:
    return '%sT23:59:59Z' % date


def extract_month_from_date(date) -> int:
    value = datetime.datetime.strptime(date, date_format_in_yyyy_mm_dd)
    return value.month


def get_min_and_max_of_two_week_range(date) -> dict:
    today = datetime.datetime.strptime(date, date_format_in_yyyy_mm_dd)
    mid = today - datetime.timedelta(days=today.weekday())
    start = mid - datetime.timedelta(days=7)
    end = mid + datetime.timedelta(days=6)
    result = {
        'start': start,
        'end': end,
        'mid': mid
    }
    return result


def get_min_and_max_of_month_range(date) -> dict:
    today = datetime.datetime.strptime(date, date_format_in_yyyy_mm_dd)
    start = today - datetime.timedelta(days=today.day - 1)
    result = {
        'start': start.strftime(date_format_in_yyyy_mm_dd),
        'end': today.strftime(date_format_in_yyyy_mm_dd),
    }
    return result


def get_previous_and_current_date_range(date) -> dict:
    today = datetime.datetime.strptime(date, date_format_in_yyyy_mm_dd)
    start = today - datetime.timedelta(days=1)
    result = {
        'start': start,
        'end': today
    }
    return result


def start_date_time(date):
    hours = date.hour
    return datetime.datetime.utcnow() - datetime.timedelta(hours=hours)


def get_day_month_from_date(date):
    return date.strftime(date_format_in_dd_mm)


def get_abb_year_from_date(date):
    return date.strftime(date_format_in_yyyy)


def get_date_from_string(date):
    return datetime.datetime.strptime(date, date_format_in_yyyy_mm_dd_hh_mm_ss)


def date_from_datetime(date_time):
    return date_time.date().isoformat()


def get_date_from_string_with_timezone(date, tz=None):
    if tz is None:
        return datetime.datetime.strptime(date, date_format_in_yyyy_mm_dd_hh_mm_ss).astimezone(timezone(ist_timezone))
    else:
        return datetime.datetime.strptime(date, date_format_in_yyyy_mm_dd_hh_mm_ss).astimezone(timezone(tz))


def get_day_month_from_date_with_timezone(date, tz=None):
    LOG.info('***************************************************** %s' % date)
    if tz:
        return date.astimezone(timezone(tz)).strftime(date_format_in_dd_mm)
    else:
        return date.astimezone(timezone(ist_timezone)).strftime(date_format_in_dd_mm)


def minutes_after_now(minutes):
    return datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)

