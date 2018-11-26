from utils import (is_business_day, is_holiday, next_business_nonholilday, 
                   last_business_nonholiday, expiration_date, one_month_later)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

#Simulation configuration
start_date = pd.datetime(2008, 1, 1)
termination_date = pd.datetime(2010, 1, 1)
threshold = 0.02
rebalance_period = 20

#Commodity configuration
first_exchange = "CME"
first_commodity_ticker = "CL"
first_commodity_name = "WTI"
second_exchange = "ICE"
second_commodity_code = "B"
second_commodity_name = "BRENT"

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
    
    
cl1 = read_data(first_exchange,first_commodity_ticker, 1)
# cl2 = read_data('CME', 'CL', 2)
cl7 = read_data(first_exchange,first_commodity_ticker, 7)
b1 = read_data(second_exchange,second_commodity_code, 1)
# b2 = read_data('ICE', 'B', 2)
b7 = read_data(second_exchange,second_commodity_code, 7)
cb = pd.concat([cl1, b1], axis=1, join='inner')

# Initialization of Parameters
cl_pos = 0
b_pos = 0
pnl = 0
pnl_ls = []
day_count = 0 # The way the code structured now, only trading days are counted.
previous_price1 = 0
previous_price2 = 0
position = 0 # This is the indicator of whether we are holding positions, if
# we are during rolling period and not holding anything, this would also be 1

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
            pnl_ls.append([dt, pnl])
            
            # Check if it's time to roll
            # If both contracts have non-zero positions
            if abs(cl_pos - b_pos) == 2:
                # If it's at or after the second preceding business day, 
                # we begin to roll our contract. We record our position now, 
                # and set the current position to be zero
                if dt >= last_business_nonholiday(exp_cl, 2):
                    cl_pos = 0
                    previous_cl_pos = cl_pos
                if dt >= last_business_nonholiday(exp_b, 2):
                    b_pos = 0
                    previous_b_pos = b_pos
            # If one of the contracts have zero position, this means that one
            # of the contract is waiting to be rolled. Check if it's time to
            # enter the new front month contract
            # A problem exist here. Is this expiration date the passed one, or
            # it has been changed to the next month's
            elif abs(cl_pos - b_pos) == 1:
                if cl_pos == 0:
                    if dt >= next_business_nonholilday(exp_cl, 2):
                        cl_pos = previous_cl_pos
                else:
                    if dt >= next_business_nonholilday(exp_b, 2):
                        b_pos = previous_b_pos
            # If both of the positions are zero, then it could be that both of 
            # contracts are waiting to be rolled. It can also be that the 
            # signal didn't hit the threshold.
            else:
                # If the position equals 1, it means that both contracts 
                # are waiting to be rolled
                if position == 1:
                    if dt >= next_business_nonholilday(exp_cl, 2):
                        cl_pos = previous_cl_pos
                    if dt >= next_business_nonholilday(exp_b, 2):
                        b_pos = previous_b_pos
        
        # Every rebalance period, we recalculate the signals
        if day_count % rebalance_period == 0:
            cl_sgn = signal(cl1.loc[dt][0], cl7.loc[dt][0], 6)
            b_sgn = signal(b1.loc[dt][0], b7.loc[dt][0], 6)
            # If the signal > threshold, we consider opening positions
            if abs(cl_sgn - b_sgn) > threshold:
                # Then check the expiration date
                exp_cl = expiration_date(dt.year, dt.month,first_commodity_name)
                exp_b = expiration_date(dt.year, dt.month,second_commodity_name)
                # If the date is at least three business days before the 
                # expiration date, we open the position.
                if (dt <= last_business_nonholiday(exp_cl, 3) and 
                    dt <= last_business_nonholiday(exp_b, 3)):
                    cl_pos = np.sign(cl_sgn - b_sgn)
                    b_pos = -cl_pos
                    position = 1
                # If the date is at the two days after the expiration date, we 
                # change the expiration date to that of next month's contract
                elif (dt >= next_business_nonholilday(exp_cl, 2) and 
                      dt >= next_business_nonholilday(exp_b, 2)):
                    cl_pos = np.sign(cl_sgn - b_sgn)
                    b_pos = -cl_pos
                    y, m = one_month_later(dt.year, dt.month)
                    exp_cl = expiration_date(y, m,first_commodity_name)
                    exp_b = expiration_date(y, m,second_commodity_name)
                    position = 1
                # If neither of that condition is met, we do nothing
                else:
                    cl_pos = 0
                    b_pos = 0
                    position = 0
            else:
                cl_pos = 0
                b_pos = 0                                
                position = 0    
        if cl_pos - b_pos != 0:
            previous_price1 = cl1.loc[dt][0]
            previous_price2 = b1.loc[dt][0]
            day_count += 1

    dt = next_business_nonholilday(dt, 1)
    
pnl_df = pd.DataFrame(pnl_ls, columns=['date', 'pnl'])

output_name = ' '.join([first_commodity_name,second_commodity_name,start_date.strftime("%b %d, %Y"),"to",termination_date.strftime("%b %d, %Y"),'.csv'])
pnl_df.to_csv(output_name)
