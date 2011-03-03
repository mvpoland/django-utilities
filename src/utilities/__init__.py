VERSION = (0, 1,)

# Dynamically calculate the version based on VERSION tuple
if len(VERSION)>2 and VERSION[2] is not None:
    str_version = "%s.%s_%s" % VERSION[:3]
else:
    str_version = "%s.%s" % VERSION[:2]

__version__ = str_version

import datetime

def is_years_ago(verify_date, years, start_date=None):
    if start_date is None:
        if isinstance(verify_date, datetime.datetime):
            start_date = datetime.datetime.now()
        else:
            start_date = datetime.date.today()

    try:
        start_date = start_date.replace(year=start_date.year - years)
    except ValueError:
        if start_date.month == 2 and start_date.day == 29:
            start_date = start_date.replace(month=2, day=28,
                                            year=start_date.year - years)

    return (verify_date - start_date).days > 0