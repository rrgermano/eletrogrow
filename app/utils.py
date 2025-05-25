import datetime
import time
import pandas_market_calendars as mcal
from dateutil.relativedelta import relativedelta

def is_date_util(date, delta="Positive"):
    try:
        date = date.date()
    except:
        pass
    calendar = mcal.get_calendar("BMF")
    util_days = calendar.schedule(start_date=datetime.datetime.strftime(date - relativedelta(days=7),
                                                                           '%Y-%m-%d'),
                                     end_date=datetime.datetime.strftime(date + relativedelta(days=7),
                                                                         '%Y-%m-%d'))
    while datetime.datetime.fromtimestamp(time.mktime(date.timetuple())) not in util_days.index:
        if delta.capitalize() == "Positive":
            date = date + relativedelta(days=1)
        else:
            date = date - relativedelta(days=1)
    return date


def credit_period(requested_month=None):
    if not requested_month:
        requested_month = datetime.date.today()

    today = requested_month

    if (today + relativedelta(days=7)) <= is_date_util(today.replace(day=3) + relativedelta(months=1)):
        requested_month = today
    elif today.day > today.replace(day=3):
        requested_month = today+relativedelta(months=1)
    else:
        requested_month = today


    return {
        'initial': (
                    is_date_util(requested_month.replace(day=3)) - relativedelta(days=7),
                    requested_month.strftime('%B/%Y')
                    ),
        'closing': (
                    is_date_util((requested_month+relativedelta(months=1)).replace(day=3)) - relativedelta(days=7),
                    requested_month.strftime('%B/%Y')
                    )
            }
