import dateutil.parser
from dateutil import tz


def ordinal(num):
    """
      Returns ordinal number string from int,
      e.g. 1, 2, 3 becomes 1st, 2nd, 3rd, etc.
    """
    number = num
    n = int(number)
    if 4 <= n <= 20:
        suffix = 'th'
    elif n == 1 or (n % 10) == 1:
        suffix = 'st'
    elif n == 2 or (n % 10) == 2:
        suffix = 'nd'
    elif n == 3 or (n % 10) == 3:
        suffix = 'rd'
    elif n < 100:
        suffix = 'th'
    ord_num = str(n) + suffix
    return ord_num


def ordinal_output(time):
    from_zone = tz.tzlocal()
    to_zone = tz.tzutc()
    d = dateutil.parser.parse(time)
    d = d.replace(tzinfo=from_zone)
    d = d.astimezone(to_zone)
    ord_number = d.strftime('%d')
    ordinal_res = ordinal(ord_number)
    dt = ordinal_res + d.strftime(' %B %Y-%H:%M %p UTC')
    return dt


def ordinal_output2(time):
    # from_zone = tz.tzutc()
    # to_zone = tz.tzlocal()
    d = dateutil.parser.parse(time)
    # d = d.replace(tzinfo=from_zone)
    # d = d.astimezone(to_zone)
    ord_number = d.strftime('%d')
    ordinal_res = ordinal(ord_number)
    dt = ordinal_res + d.strftime(' %B %Y-%H:%M %p UTC')
    return dt
