# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 11:33:10 2018
@author: Kai, Phil
"""
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar as calendar
from pandas.tseries.offsets import BDay
import datetime
from calendar import monthrange
from dateutil.relativedelta import relativedelta

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
    
# Give the expriation date of a given year and month as per contract specs   
def expiration_date(year,month,commodity):
    if commodity == "WTI":
        #CME WTI crude oil future
        t1 = datetime.datetime(year, month, 25)
        if is_business_day(t1) and not is_holiday(t1):
            decrement = 3
        else:
            decrement = 4
    elif commodity == "BRENT":
        #ICE Brent oil future
        days_in_month = monthrange(year,month)[1]
        t1 = datetime.datetime(year,month,days_in_month)
        if is_business_day(t1) and not is_holiday(t1):
            decrement = 0
        else:
            decrement = 1
    elif commodity == "NG":
        #CME Henry Hub natural gas
        days_in_month = monthrange(year,month)[1]
        t1 = datetime.datetime(year,month,days_in_month)
        if is_business_day(t1) and not is_holiday(t1):
            decrement = 2
        else:
            decrement = 3
    elif commodity == "UKNG":
        #UK natural gas futures
        days_in_month = monthrange(year,month)[1]
        t1 = datetime.datetime(year,month,days_in_month)
        if is_business_day(t1) and not is_holiday(t1):
            decrement = 1
        else:
            decrement = 2
    elif commodity == "RBOBGAS":
        #RBOB gasoline
        days_in_month = monthrange(year,month)[1]
        t1 = datetime.datetime(year,month,days_in_month)
        if is_business_day(t1) and not is_holiday(t1):
            decrement = 0
        else:
            decrement = 1
    elif commodity == "GASOIL":
        #ICE gas oil futures
        t1 = datetime.datetime(year, month, 14)
        decrement = 2
    elif commodity == "HEATOIL":
        #NY Harbor heating oil
        days_in_month = monthrange(year,month)[1]
        t1 = datetime.datetime(year,month,days_in_month)
        if is_business_day(t1) and not is_holiday(t1):
            decrement = 0
        else:
            decrement = 1
    else:
        return -1
    exd = last_business_nonholiday(t1,decrement)
    return exd

#==============================================================================
# for i in range(12, 0, -1):
#     print(expiration_date(2014, i))
#==============================================================================
