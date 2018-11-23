import quandl, numpy, math, datetime
from dateutil.relativedelta import relativedelta
from utils import expiration_date, is_business_day, is_holiday
quandl.ApiConfig.api_key = "tjxFewEnckmn8zjjsHSZ"

"""
Created on Thanksgibbin' at around 11PM
@author: Phil
"""

def trade_signal(signal_date):

    #Confirms signal_date is not a business day or holiday
    if not is_business_day(signal_date) or (is_holiday(signal_date)):
        return -1

    #Converts the date to the right format and fetches the first and seventh future
    if signal_date.month <10:
        signal_date_month_string = ''.join(["0",str(signal_date.month)])
    else:
        signal_date_month_string = str(signal_date.month)
        
    if signal_date.day < 10:
        signal_date_day_string = ''.join(["0",str(signal_date.day)])
    else:
        signal_date_day_string = str(signal_date.day)
        
    signal_date_string = ''.join(['"',str(signal_date.year),'-',str(signal_date.month),'-',signal_date_day_string,'"'])
##    print(signal_date_string)

    near = quandl.get("CHRIS/CME_CL1",start_date=signal_date_string,end_date=signal_date_string,returns="numpy")
    for item in near:
        near_price = float(item[4])
##        print(near_price)

    far = quandl.get("CHRIS/CME_CL7",start_date=signal_date_string,end_date=signal_date_string,returns="numpy")
    for item in far:
        far_price = float(item[4])
##        print(far_price)

    #Figures out the dates of the the near and far futures, days between the two dates
    near_date = expiration_date(signal_date.year,signal_date.month)
    far_date = near_date + relativedelta(months=+6)
    far_date = expiration_date(far_date.year,far_date.month)
##    print(near_date)
##    print(far_date)
    if near_date.date() <= signal_date:
##        print(True)
        near_date = near_date + relativedelta(months=+1)
        far_date = far_date + relativedelta(months=+1)
##        print(near_date)
##        print(far_date)
    delta = far_date - near_date
##    print(delta.days)

    #Calculates the signal and returns it
    signal = (math.log(near_price) - math.log(far_price)) * 365 / delta.days
    return signal