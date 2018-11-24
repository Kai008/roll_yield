# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 11:33:10 2018

@author: Kai
"""
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar as calendar
from pandas.tseries.offsets import BDay
import datetime

# Determine if a date is a holiday
def is_holiday(date):
    cal = calendar()
    st = datetime.datetime(date.year, date.month, 1)
    ed = st + datetime.timedelta(days=31)
    hols = cal.holidays(start=st, end=ed)
    if date in hols:
        return True
    else:
        return False
        
# Determine if a date is a business day
def is_business_day(date):
    if date.weekday()+1 in set((1,2,3,4,5)):
        return True
    else:
        return False

# Give the date that is "num" business days prior to a date. When counting back, 
# holidays does not count
def last_business_nonholiday(date, num):
    for i in range(num):
        date -= BDay(1)
        while(is_holiday(date)):
            date -= BDay(1)
    return date

# Give the date that is "num" business days after a date. When counting forward, 
# holidays does not count
def next_business_nonholilday(date, num):
    for i in range(num):
        date += BDay(1)
        while(is_holiday(date)):
            date += BDay(1)
    return date
    
# Give the expriation date of a given year and month    
def expiration_date(year, month):
    t1 = datetime.datetime(year, month, 25)
    if is_business_day(t1) and not is_holiday(t1):
        exd = last_business_nonholiday(t1, 3)
    else:
        exd = last_business_nonholiday(t1, 4)
        
    return exd

#==============================================================================
# for i in range(12, 0, -1):
#     print(expiration_date(2014, i))
#==============================================================================
    
