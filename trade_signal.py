import quandl, numpy, math, datetime
from dateutil.relativedelta import relativedelta
from utils import expiration_date, is_business_day, is_holiday
quandl.ApiConfig.api_key = "tjxFewEnckmn8zjjsHSZ"

"""
Updated Friday November 23, 2018 at ~4PM
@author: Phil
"""

def trade_signal(signal_date,commodity,months_ahead):

    #Confirms signal_date is not a business day or holiday
    if not is_business_day(signal_date) or (is_holiday(signal_date)):
        return -1

    #Finds the near and far commodity ticker
    #Crude oil
    if commodity == "WTI":
        #WTI crude
        near_commodity = "CHRIS/CME_CL1"
        far_commodity = ''.join(["CHRIS/CME_CL",str(months_ahead+1)])
    elif commodity == "BRENT":
        #Brent crude
        near_commodity = "CHRIS/ICE_B1"
        far_commodity = ''.join(["CHRIS/ICE_B",str(months_ahead+1)])
    #Natural gas
    elif commodity == "NG":
        #US natural gas
        near_commodity = "CHRIS/CME_NG1"
        far_commodity = ''.join(["CHRIS/CME_NG",str(months_ahead+1)])
    elif commodity == "UKNG":
        #UK natural gas
        near_commodity = "CHRIS/ICE_M1"
        far_commodity = ''.join(["CHRIS/ICE_M",str(months_ahead+1)])
    #Cattle
    elif commodity == "LC":
        #Live cattle
        near_commodity = "CHRIS/CME_LC1"
        far_commodity = ''.join(["CHRIS/CME_LC",str(months_ahead+1)])
    elif commodity == "FC":
        #Feeder cattle
        near_commodity = "CHRIS/CME_FC1"
        far_commodity = ''.join(["CHRIS/CME_FC",str(months_ahead+1)])
    #Distillates
    elif commodity == "RBOBGAS":
        #RBOB Gas
        near_commodity = "CHRIS/CME_RB1"
        far_commodity = ''.join(["CHRIS/CME_RB",str(months_ahead+1)])
    elif commodity == "GASOIL":
        #Gas oil
        near_commodity = "CHRIS/ICE_G1"
        far_commodity = ''.join(["CHRIS/ICE_G",str(months_ahead+1)])
    elif commodity == "HEATOIL":
        #Heating oil
        #Only goes out to the fourth month (fifth future)
        near_commodity = "CHRIS/ICE_O1"
        far_commodity = ''.join(["CHRIS/ICE_O",str(months_ahead+1)])
    #Wheat
    elif commodity == "WHEAT":
        #Plain ol' wheat
        near_commodity = "CHRIS/CME_W1"
        far_commodity = ''.join(["CHRIS/CME_W",str(months_ahead+1)])
    elif commodity == "KWHEAT":
        #Kansas City hard red wheat
        #Only goes out to the fifth month (sixth future)
        near_commodity = "CHRIS/CME_KW1"
        far_commodity = ''.join(["CHRIS/CME_KW",str(months_ahead+1)])
    elif commodity == "MWHEAT":
        #Milling wheat
        #Only goes out to the fifth month (sixth future)
        near_commodity = "CHRIS/LIFFE_EBM1"
        far_commodity = ''.join(["CHRIS/LIFFE_EBM",str(months_ahead+1)])
    #Catch all for commodities not on the list
    else:
        return -1

    #Converts the date to the right format and fetches the near and far future
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

    near = quandl.get(near_commodity,start_date=signal_date_string,end_date=signal_date_string,returns="numpy")
    for item in near:
        near_price = float(item[4])
##        print(near_price)

    far = quandl.get(far_commodity,start_date=signal_date_string,end_date=signal_date_string,returns="numpy")
    for item in far:
        far_price = float(item[4])
##        print(far_price)

    #Figures out the dates of the the near and far futures, days between the two dates
    near_date = expiration_date(signal_date.year,signal_date.month)
    far_date = near_date + relativedelta(months=+months_ahead)
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
