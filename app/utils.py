import datetime
import time
import pandas_market_calendars as mcal
from dateutil.relativedelta import relativedelta

def is_date_util(date, delta="Positive"):
    try:
        date = date.date()
    except:
        pass
    calendario = mcal.get_calendar("BMF")
    dias_uteis = calendario.schedule(start_date=datetime.datetime.strftime(date - relativedelta(days=7),
                                                                           '%Y-%m-%d'),
                                     end_date=datetime.datetime.strftime(date + relativedelta(days=7),
                                                                         '%Y-%m-%d'))
    while datetime.datetime.fromtimestamp(time.mktime(date.timetuple())) not in dias_uteis.index:
        if delta.capitalize() == "Positive":
            date = date + relativedelta(days=1)
        else:
            date = date - relativedelta(days=1)
    return date