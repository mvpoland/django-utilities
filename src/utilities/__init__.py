VERSION = (0, 1,)

# Dynamically calculate the version based on VERSION tuple
if len(VERSION) > 2 and VERSION[2] is not None:
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

def sorted_dict(adict, reverse=False):
    keys = adict.keys()
    keys.sort(reverse=reverse)
    return map(adict.get, keys)

def whole_number(number):
    """
    If the value has no decimal value then we convert to int. This looks nicer
    
    """

    if number % 1 == 0:
        return int(number)
    return number

class EnrichedIterable(object):
    """
    Enricher for an iterable object. The enrich method will be called as late
    as possible. (On retrieval of a single item.)
    """
    def __init__(self, iterable, enrich_func):
        self.iterable = iterable
        self.enrich_func = enrich_func

    class Iterator(object):
        def __init__(self, iterator, enrich_func):
            self.iterator = iterator
            self.enrich_func = enrich_func

        def next(self):
            item = self.iterator.next()
            self.enrich_func(item)
            return item

    def __getitem__(self, k):
        if isinstance(k, slice):
            return EnrichedIterable(self.iterable[k], self.enrich_func)
        else:
            item = self.iterable[k]
            self.enrich_func(item)
            return item

    def __iter__(self):
        return EnrichedIterable.Iterator(self.iterable.__iter__(), self.enrich_func)

    def __len__(self):
        return len(self.iterable)
