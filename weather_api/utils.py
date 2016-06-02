from datetime import datetime, timedelta
import pytz

def input_datetime(string):
    """
    Handles an ISO-format input date string in UTC only, format like
    YY-MM-DDTHH:MM:SSZ or YY-MM-DDTHH:MM:SS+00:00
    Returns a timezone-aware UTC datetime object.
    """
    if string[-1] == 'Z':
        conv = datetime.strptime(string, "%Y-%m-%dT%H:%M:%SZ")
    elif string[-6:] == "+00:00":
        conv = datetime.strptime(string, "%Y-%m-%dT%H:%M:%S+00:00")
    else:
        raise ValueError("Invalid string TZ type in {}".format(string))

    tz = pytz.timezone('UTC')
    return tz.localize(conv)

def input_date(string):
    """
    Handles an ISO-format date string, format like YY-MM-DD
    Returns a timezone-aware UTC datetime object of midnight on that day.
    """
    conv = datetime.strptime(string, "%Y-%m-%d")

    tz = pytz.timezone('UTC')
    return tz.localize(conv)
