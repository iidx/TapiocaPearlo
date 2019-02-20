from datetime import datetime

import math


def to_datetime(timestamp, timezone=0):
    """Convert timestamp into datetime."""
    # change timestamp type if type is string 
    if type(timestamp) is str:
        timestamp = int(timestamp)

    if type(timestamp) is int:
        if timestamp <= 0:
            timestamp = 0

        elif int(math.log10(timestamp)) + 1 > 10:
            timestamp = int(timestamp / 1000)

    return datetime.utcfromtimestamp(timestamp)
