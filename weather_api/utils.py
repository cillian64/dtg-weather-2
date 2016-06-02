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
    if string is None or string.lower() == "today":
        conv = datetime.now()
        conv = conv.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        conv = datetime.strptime(string, "%Y-%m-%d")

    tz = pytz.timezone('UTC')
    return tz.localize(conv)

def winddir(bearing):
    """
    Converts a bearing to a character format, e.g. 0 -> 'N', 45 -> 'NE'
    """
    if bearing < 0 or bearing > 360:
        raise ValueError("Invalid bearing")

    text = ""
    if bearing >= 292.5 or bearing < 67.5:
        text += "N"
    elif bearing >= 112.5 and bearing < 245.5:
        text += "S"
    if bearing >= 22.5 and bearing < 157.5:
        text += "E"
    elif bearing >= 202.5 and bearing < 337.5:
        text += "W"
    return text

