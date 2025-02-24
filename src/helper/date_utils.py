import datetime

def timestamp_as_time(timestamp):

    return datetime.datetime.fromtimestamp(timestamp, tz=datetime.UTC)
