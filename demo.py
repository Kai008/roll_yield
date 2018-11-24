# -*- coding: utf-8 -*-
"""
Created on Fri Nov 23 15:50:57 2018

@author: Kai
"""

from utils import is_business_day, is_holiday, next_business_nonholilday
import pandas as pd
import math

start_date = pd.datetime(2010, 1, 1)
termination_date = pd.datetime(2012, 1, 1)
threshold = 0.04
rebalance_period = 10

def read_data(exchange, code, month):
    df = pd.read_csv("../data/CHRIS-"+exchange+"_"+code+str(month)+".csv")
    try:
        lp = df[['Last']]
    except KeyError as e:
        lp = df[['Settle']]
    lp.index = pd.to_datetime(df['Date'])
    return lp

def signal(near_price, far_price, month_ahead):
    return (math.log(near_price) - math.log(far_price)) * 365 / (30*month_ahead)
    
    
cl1 = read_data('CME', 'CL', 1)
cl7 = read_data('CME', 'CL', 7)
b1 = read_data('ICE', 'B', 1)
b7 = read_data('ICE', 'B', 7)
cb = pd.concat([cl1, b1], axis=1, join='inner')

# Initialization of Parameters
cl_pos = 0
b_pos = 0
pnl = 0
day_count = 0 # The way the code structured now, only trading days are counted.
previous_price1 = 0
previous_price2 = 0

if is_holiday(start_date) or not is_business_day(start_date):
    dt = next_business_nonholilday(start_date, 1)
else:
    dt = start_date


# Executing the Roll Yield Strategy    
while(dt < termination_date):    
    # Calculating PnL
    if dt in cb.index:
        if day_count != 0:
            pnl += cl_pos * (cl1.loc[dt][0] - previous_price1) 
            + b_pos * (b1.loc[dt][0] - previous_price2)
        
        if day_count % rebalance_period == 0:
            cl_sgn = signal(cl1.loc[dt][0], cl7.loc[dt][0], 6)
            b_sgn = signal(b1.loc[dt][0], b7.loc[dt][0], 6)
            if cl_sgn - b_sgn > threshold:
                cl_pos = 1
                b_pos = -1
            elif cl_sgn - b_sgn < -threshold:
                cl_pos = -1
                b_pos = 1
            else:
                cl_pos = 0
                b_pos = 0
        
        previous_price1 = cl1.loc[dt][0]
        previous_price2 = b1.loc[dt][0]
        day_count += 1

    dt = next_business_nonholilday(dt, 1)
    
print("Profit and Loss: ", pnl)
    