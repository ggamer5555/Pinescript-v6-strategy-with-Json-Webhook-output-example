import MetaTrader5 as mt5
import pandas as pd


import asyncio, json, time # , websockets, requests
from termcolor import colored
import numpy as np
import decimal
import sqlite3
import threading
from tabulate import tabulate

import logging
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter

from datetime import datetime, timedelta

import math


import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
from datetime import datetime, timedelta
from matplotlib.animation import FuncAnimation
import matplotlib
matplotlib.use('agg')

import subprocess
import sys

# def run_worker_program():
#     # Replace 'other_program.py' with the name of your Python file
#     process = subprocess.Popen(['python', 'worker.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#     # Wait for the process to finish and get its return code
#     stdout, stderr = process.communicate()

#     # Print the output of the other program
#     print(stdout.decode('utf-8'))

#     # Print any errors
#     print(stderr.decode('utf-8'))

#     # Get the return code
#     return_code = process.returncode
#     print("Return code:", return_code)

def run_chart_program():
    # Replace 'other_program.py' with the name of your Python file
    process = subprocess.Popen(['python', 'chart_equity_live.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for the process to finish and get its return code
    stdout, stderr = process.communicate()

    # Print the output of the other program
    print(stdout.decode('utf-8'))

    # Print any errors
    print(stderr.decode('utf-8'))

    # Get the return code
    return_code = process.returncode
    print("Return code:", return_code)


def run_wsgi_program():
    # Replace 'other_program.py' with the name of your Python file
    process = subprocess.Popen(['python', 'wsgi.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for the process to finish and get its return code
    stdout, stderr = process.communicate()

    # Print the output of the other program
    print(stdout.decode('utf-8'))

    # Print any errors
    print(stderr.decode('utf-8'))

    # Get the return code
    return_code = process.returncode
    print("Return code:", return_code)


# added if i want to skip first order for FTUK no_first_order variable
# added so it doesnt double order if no_first_order == 1
# added trading allowed times different for sunday 00:05 and 23:40  01:05 and 23:40 sunday
# added when to close trade when threshold met different for friday 23:00 and 23:54 22:00 and 23:54 friday
# added threshold to open trade 

# SL TP UPDATE changed so it updates only if the TP number is different to current TP
# added delete ticket if found in history_deels

# posible bug with limit order placement incriment
# posible bug with reset norm_active ater orders closed

# added live_price is less or more that order price so no error occur  

# added  and dd_daily_active == 0 complete
# added total_risk_active to if statements

#added rounding down lot sizes 
    



total_risk_active = 0
input_risk_total_global = 10 #2 is max upto 5 daily dd sooo
dd_daily_active = 0
dd_percentage = 0
symbol = 'BTCUSD'
deals_in_history = 0
number_of_days_before_account_inactive = 25 #30 in reality
min_order_size_lot = 0.01
max_daily_dd_percentage = 3 #5 is max upto 5 daily dd sooo
risk_total_global = 0
no_first_order = 0
time_close_threshhold = 0.12 / 100 #0.1%
time_open_threshhold_bbw = 0.25 / 100 #0.2%
time_open_threshhold_norm = 0.6 / 100 #0.2%
time_open_threshhold_oi = 0.6 / 100 #0.2%
count_oi_output = 0
max_drawdown = 0

oi_needs_reset = 0
bbw_needs_reset = 0
norm_needs_reset = 0

equity_data = []

initial_order_price = 0
initial_order_price_short = 0
initial_order_price_bbw = 0
initial_order_price_short_bbw = 0

account_balance = 100000 #10000
base_order_norm = 1.3
order_size_norm = account_balance * (base_order_norm/100)

base_order_bbw = 40
order_size_bbw = account_balance * (base_order_bbw/100)

base_order_oi = 2.9
order_size_oi = account_balance * (base_order_oi/100)


#strategy.equity*base_order/100
#strategy.equity*safe_order/100* math.pow(safe_order_volume_scale,(current_so-1)
deviation_percentage = 0.22 / 100 # 0.5% deviation
max_dca_orders = 5
dca_orders = 0  # Counter for DCA orders placed

deviation_percentage_short = 0.25 / 100 # 0.5% deviation
max_dca_orders_short = 5
dca_orders_short = 0  # Counter for DCA orders placed

deviation_percentage_bbw = 0.22 / 100 # 0.5% deviation
max_dca_orders_bbw = 3
dca_orders_bbw = 0  # Counter for DCA orders placed

deviation_percentage_short_bbw = 0.22 / 100 # 0.5% deviation
max_dca_orders_short_bbw = 3
dca_orders_short_bbw = 0  # Counter for DCA orders placed

deviation_percentage_oi = 0.01 / 100 # 0.5% deviation
max_dca_orders_oi = 5
dca_orders_oi = 0  # Counter for DCA orders placed

deviation_percentage_short_oi = 0.01 / 100 # 0.5% deviation
max_dca_orders_short_oi = 5
dca_orders_short_oi = 0  # Counter for DCA orders placed



# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish MetaTrader 5 connection to a specified trading account
if not mt5.initialize(login=1052240340, server="FTMO-Demo",password="example"):
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# display data on connection status, server name and trading account
print(mt5.terminal_info())
# display data on MetaTrader 5 version
print(mt5.version())




current_time = datetime.now()
# Add two hours to the current time
time_plus_two_hours = current_time + timedelta(hours=2)

time_active = 0
# Check if time_plus_two_hours is between 23:00 and 23:54 any day
if time_plus_two_hours.hour == 23 and 0 <= time_plus_two_hours.minute <= 54:
    time_active = 1

    # Check if time_plus_two_hours is between 22:00 and 23:54 friday
if current_time.weekday() == 4 and (time_plus_two_hours.hour == 22 or (time_plus_two_hours.hour == 23 and 0 <= time_plus_two_hours.minute <= 54)):
    time_active = 1

# Check if it's Sunday and time is between 01:05 and 23:40
if time_plus_two_hours.weekday() == 6 and (time_plus_two_hours.hour > 1 or (time_plus_two_hours.hour == 1 and time_plus_two_hours.minute >= 6)) and (time_plus_two_hours.hour < 23 or (time_plus_two_hours.hour == 23 and time_plus_two_hours.minute <= 40)):
    orders_can_be_placed = 1
# Check if time is between 00:05 and 23:40 (for all other days) no sunday
elif time_plus_two_hours.weekday() != 6 and (time_plus_two_hours.hour > 0 or (time_plus_two_hours.hour == 0 and time_plus_two_hours.minute >= 6)) and (time_plus_two_hours.hour < 23 or (time_plus_two_hours.hour == 23 and time_plus_two_hours.minute <= 40)):
    orders_can_be_placed = 1
else:
    orders_can_be_placed = 0

print("Current time:", current_time)
print("Time plus two hours:", time_plus_two_hours)
# print("Time active:", time_active)





spread_now = ((mt5.symbol_info_tick(symbol).ask - mt5.symbol_info_tick(symbol).bid) / mt5.symbol_info_tick(symbol).ask) * 100
live_price =  mt5.symbol_info_tick(symbol).bid

global initial_lot_size, current_lot_size, initial_lot_size_short, current_lot_size_short
global initial_lot_size_bbw, current_lot_size_bbw, initial_lot_size_short_bbw, current_lot_size_short_bbw
global initial_lot_size_oi, current_lot_size_oi, initial_lot_size_short_oi, current_lot_size_short_oi


initial_lot_size = order_size_norm / live_price 
current_lot_size = initial_lot_size
#current_lot_size = round(current_lot_size, 2)
current_lot_size = math.floor(current_lot_size * 100) / 100 # round down 2 decimals

initial_lot_size_short = order_size_norm / live_price 
current_lot_size_short = initial_lot_size_short
###current_lot_size_short = round(current_lot_size_short, 2)
current_lot_size_short = math.floor(current_lot_size_short * 100) / 100 # round down 2 decimals

initial_lot_size_bbw = order_size_bbw / live_price 
current_lot_size_bbw = initial_lot_size_bbw
#current_lot_size_bbw = round(current_lot_size_bbw, 2)
current_lot_size_bbw = math.floor(current_lot_size_bbw * 100) / 100 # round down 2 decimals

initial_lot_size_short_bbw = order_size_bbw / live_price 
current_lot_size_short_bbw = initial_lot_size_short_bbw
#current_lot_size_short_bbw = round(current_lot_size_short_bbw, 2)
current_lot_size_short_bbw = math.floor(current_lot_size_short_bbw * 100) / 100 # round down 2 decimals

initial_lot_size_oi = order_size_oi / live_price 
current_lot_size_oi = initial_lot_size_oi
#current_lot_size_oi = round(current_lot_size_oi, 2)
current_lot_size_oi = math.floor(current_lot_size_oi * 100) / 100 # round down 2 decimals

initial_lot_size_short_oi = order_size_oi / live_price 
current_lot_size_short_oi = initial_lot_size_short_oi
#current_lot_size_short_oi = round(current_lot_size_short_oi, 2)
current_lot_size_short_oi = math.floor(current_lot_size_short_oi * 100) / 100 # round down 2 decimals









# Function to fetch all order ticket values from the database
def fetch_order_tickets():
    conn = sqlite3.connect('tickets.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM order_tickets_norm_L")
    rows_L = cursor.fetchall()  # Fetch results for L
    cursor.execute("SELECT * FROM order_tickets_norm_S")
    rows_S = cursor.fetchall()  # Fetch results for S
    conn.close()
    return rows_L + rows_S  # Concatenate the results

# Fetch all order ticket values
order_tickets = fetch_order_tickets()

# If there are no tickets, clear norm_active and set to 0
if not order_tickets:
    print('norm_active cleared')
    conn = sqlite3.connect('memory_live_entries_DB.sqlite')
    cursor = conn.cursor()
    cursor.execute("UPDATE norm_active SET norm_active = ?", (0,))
    conn.commit()
    conn.close()


def fetch_order_tickets():
    conn = sqlite3.connect('tickets_bbw.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM order_tickets_bbw_L")
    rows_L = cursor.fetchall()  # Fetch results for L
    cursor.execute("SELECT * FROM order_tickets_bbw_S")
    rows_S = cursor.fetchall()  # Fetch results for S
    conn.close()
    return rows_L + rows_S  # Concatenate the results

# Fetch all order ticket values
order_tickets = fetch_order_tickets()

# If there are no tickets, clear norm_active and set to 0
if not order_tickets:
    print('bbw_active cleared')
    conn = sqlite3.connect('memory_live_entries_DB.sqlite')
    cursor = conn.cursor()
    cursor.execute("UPDATE bbw_active SET bbw_active = ?", (0,))
    conn.commit()
    conn.close()


def fetch_order_tickets():
    conn = sqlite3.connect('tickets_OI.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM order_tickets_oi_L")
    rows_L = cursor.fetchall()  # Fetch results for L
    cursor.execute("SELECT * FROM order_tickets_oi_S")
    rows_S = cursor.fetchall()  # Fetch results for S
    conn.close()
    return rows_L + rows_S  # Concatenate the results

# Fetch all order ticket values
order_tickets = fetch_order_tickets()

# If there are no tickets, clear norm_active and set to 0
if not order_tickets:
    print('oi_active cleared')
    conn = sqlite3.connect('memory_live_entries_DB.sqlite')
    cursor = conn.cursor()
    cursor.execute("UPDATE oi_active SET oi_active = ?", (0,))
    conn.commit()
    conn.close()


def get_equity_daily_drawdown():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('equity_daily_drawdown.sqlite')
        cursor = conn.cursor()
        
        # Select the equitydd value from the equitydd table
        cursor.execute("SELECT equitydd FROM equitydd LIMIT 1")
        
        # Fetch the equitydd value
        max_drawdown = cursor.fetchone()[0]
        
        return max_drawdown
    
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return None
    
    except Exception as e:
        print("Error:", e)
        return None
    
    finally:
        # Close the connection in the finally block to ensure it gets closed
        if conn:
            conn.close()

# Call the function to get the equity daily drawdown
max_drawdown = get_equity_daily_drawdown()
if max_drawdown is not None:
    print("Equity Daily Drawdown:", max_drawdown)
else:
    print("Failed to retrieve Equity Daily Drawdown.")







# # Connect to the SQLite database (or create it if it doesn't exist)
# conn = sqlite3.connect('memory_live_entries_DB.sqlite')
# # Create a cursor object to execute SQL queries
# cursor = conn.cursor()
# # Update the value in the norm_active table
# cursor.execute("UPDATE oi_active SET oi_active = ?", (0,))
# conn.commit()
# conn.close()

# # Connect to the SQLite database (or create it if it doesn't exist)
# conn = sqlite3.connect('memory_live_entries_DB.sqlite')
# # Create a cursor object to execute SQL queries
# cursor = conn.cursor()
# # Update the value in the norm_active table
# cursor.execute("UPDATE bbw_active SET bbw_active = ?", (0,))
# conn.commit()
# conn.close()

# # Connect to the SQLite database (or create it if it doesn't exist)
# conn = sqlite3.connect('memory_live_entries_DB.sqlite')
# # Create a cursor object to execute SQL queries
# cursor = conn.cursor()
# # Update the value in the norm_active table
# cursor.execute("UPDATE norm_active SET norm_active = ?", (0,))
# conn.commit()
# conn.close()




##Connect to the SQLite database (or create it if it doesn't exist)
# conn = sqlite3.connect('memory_live_entries_DB.sqlite')

# # Create a cursor object to execute SQL queries
# cursor = conn.cursor()

# # Create the order_tickets_bbw_L table
# cursor.execute('''CREATE TABLE IF NOT EXISTS norm_active (
#                     norm_active
#                 )''')

# # Create the order_tickets_bbw_L table
# cursor.execute('''CREATE TABLE IF NOT EXISTS bbw_active (
#                     bbw_active
#                 )''')

# # Create the order_tickets_bbw_S table
# cursor.execute('''CREATE TABLE IF NOT EXISTS oi_active (
#                     oi_active
#                 )''')

# # Commit changes and close the connection
# conn.commit()

# # Connect to the SQLite database (or create it if it doesn't exist)
# conn = sqlite3.connect('memory_live_entries_DB.sqlite')

# # Create a cursor object to execute SQL queries
# cursor = conn.cursor()

# # Update the value in the norm_active table
# cursor.execute("UPDATE norm_active SET norm_active = ?", (0,))

# # Update the value in the bbw_active table
# cursor.execute("UPDATE bbw_active SET bbw_active = ?", (0,))

# # Update the value in the oi_active table
# cursor.execute("UPDATE oi_active SET oi_active = ?", (0,))

# # Commit changes and close the connection
# conn.commit()
# conn.close()




global initial_order_price_oi
initial_order_price_oi = 0
global initial_order_price_short_oi
initial_order_price_short_oi = 0


global side1
global side2
global side3
global dbTP1 
global dbTP2
global dbTP3
global dbSL1 
global dbSL2
global dbSL3

global ema_status


# ema_status = 1
# side1 = 0#1
# side2 = 0#1
# side3 = 0
# dbTP1 = 0#53610.0
# dbTP2 = 0#47700.0
# dbTP3 = 0
# dbSL2 = 0#44400.0
# dbSL1 = 0#43300.0
# dbSL3 = 0

# ema_status = 1
# side1 = 1
# side2 = 0#1
# side3 = 0
# dbTP1 = 53300.0
# dbTP2 = 0#47700.0
# dbTP3 = 0
# dbSL2 = 0#44400.0
# dbSL1 = 50000.0
# dbSL3 = 0

# ema_status = -1
# side1 = -1
# side2 = -1
# side3 = -1
# dbTP1 = 50000
# dbTP1 = float(dbTP1)
# dbTP2 = 50000
# dbTP2 = float(dbTP2)
# dbTP3 = 50000
# dbTP3 = float(dbTP3)
# dbSL2 = 53000
# dbSL2 = float(dbSL2)
# dbSL1 = 53000
# dbSL1 = float(dbSL1)
# dbSL3 = 53000
# dbSL3 = float(dbSL3)




# Connect to the database
conn = sqlite3.connect('memory_DB.sqlite', check_same_thread=False)

# Create a cursor
c1cc = conn.cursor()

# Fetch the first row from memory_DB table
c1cc.execute("SELECT side1, side2, side3, TP1, TP2, TP3, SL1, SL2, SL3 FROM memory_DB ORDER BY rowid ASC LIMIT 1")
first_row_memory = c1cc.fetchone()

# Fetch the first row from EMA_status table
c1cc.execute("SELECT EMA FROM EMA_status ORDER BY rowid ASC LIMIT 1")
first_row_ema_status = c1cc.fetchone()

# Close the connection
conn.close()

# Unpack the results if they exist
if first_row_memory:
    side1, side2, side3, dbTP1, dbTP2, dbTP3, dbSL1, dbSL2, dbSL3 = first_row_memory
else:
    side1 = side2 = side3 = dbTP1 = dbTP2 = dbTP3 = dbSL1 = dbSL2 = dbSL3 = None

ema_status = first_row_ema_status[0] if first_row_ema_status else None

dbTP1 = float(dbTP1)
dbTP2 = float(dbTP2)
dbTP3 = float(dbTP3)

dbSL1 = float(dbSL1)
dbSL2 = float(dbSL2)
dbSL3 = float(dbSL3)



global norm_active 
global bbw_active
global oi_active
# Connect to the SQLite database
conn = sqlite3.connect('memory_live_entries_DB.sqlite')
cursor = conn.cursor()

# Select the first value from the norm_active table
cursor.execute("SELECT norm_active FROM norm_active LIMIT 1")
norm_active = cursor.fetchone()[0]  # Fetch the value from the tuple

# Select the first value from the bbw_active table
cursor.execute("SELECT bbw_active FROM bbw_active LIMIT 1")
bbw_active = cursor.fetchone()[0]  # Fetch the value from the tuple

# Select the first value from the oi_active table
cursor.execute("SELECT oi_active FROM oi_active LIMIT 1")
oi_active = cursor.fetchone()[0]  # Fetch the value from the tuple

# Close the connection
conn.close()




# try:
#     data = [
#         [f"\033[33mdbTP1\033[0m", f"\033[33m{dbTP1}\033[0m", f"\033[33mdbTP2\033[0m", f"\033[33m{dbTP2}\033[0m", f"\033[33mdbTP3\033[0m", f"\033[33m{dbTP3}\033[0m", f"\033[32mspread\033[0m", f"\033[32m{spread_now}\033[0m"],
#         [f"\033[33mside1\033[0m", f"\033[33m{side1}\033[0m", f"\033[33mside2\033[0m", f"\033[33m{side2}\033[0m", f"\033[33mside3\033[0m", f"\033[33m{side3}\033[0m"],
#         [f"\033[31mdbSL1\033[0m", f"\033[31m{dbSL1}\033[0m", f"\033[31mdbSL2\033[0m", f"\033[31m{dbSL2}\033[0m", f"\033[31mdbSL3\033[0m", f"\033[31m{dbSL3}\033[0m"],
#         [f"\033[31mnorm_active\033[0m", f"\033[31m{norm_active}\033[0m", f"\033[31mbbw_active\033[0m", f"\033[31m{bbw_active}\033[0m", f"\033[31moi_active\033[0m", f"\033[31m{oi_active}\033[0m"],
#         [f"\033[31mema_status\033[0m", f"\033[31m{ema_status}\033[0m", f"\033[31mtime_active\033[0m", f"\033[31m{time_active}\033[0m", f"\033[31morders_can_be_placed\033[0m", f"\033[31m{orders_can_be_placed}\033[0m"],
#         #[f"\033[34m" + "bank_1_exits" + "\033[0m", f"\033[34m{float(bank_1_exits)}\033[0m", f"\033[34m" + "order_1_bank" + "\033[0m", f"\033[34m{float(order_1_bank)}\033[0m"]
#     ]
#     table = tabulate(data, tablefmt="fancy_grid")
#     print(table)
#     time.sleep(4)
# except Exception as e:
#     time.sleep(4)



#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_equity_daily_drawdown():
    global max_drawdown
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('equity_daily_drawdown.sqlite')
        cursor = conn.cursor()
        
        # Select the equitydd value from the equitydd table
        cursor.execute("SELECT equitydd FROM equitydd LIMIT 1")
        
        # Fetch the equitydd value
        max_drawdown = cursor.fetchone()[0]
        
        return max_drawdown
        
    
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return None
    
    except Exception as e:
        print("Error:", e)
        return None
    
    finally:
        # Close the connection in the finally block to ensure it gets closed
        if conn:
            conn.close()



def update_memory_DB_2():
    while True:
        time.sleep(0.2)
        global norm_active 
        global bbw_active
        global oi_active
        # Connect to the SQLite database
        conn = sqlite3.connect('memory_live_entries_DB.sqlite')
        cursor = conn.cursor()

        # Select the first value from the norm_active table
        cursor.execute("SELECT norm_active FROM norm_active LIMIT 1")
        norm_active = cursor.fetchone()[0]  # Fetch the value from the tuple

        # Select the first value from the bbw_active table
        cursor.execute("SELECT bbw_active FROM bbw_active LIMIT 1")
        bbw_active = cursor.fetchone()[0]  # Fetch the value from the tuple

        # Select the first value from the oi_active table
        cursor.execute("SELECT oi_active FROM oi_active LIMIT 1")
        oi_active = cursor.fetchone()[0]  # Fetch the value from the tuple

        # Close the connection
        conn.close()


        global max_drawdown
        # Call the function to get the equity daily drawdown
        max_drawdown = get_equity_daily_drawdown()
        if max_drawdown is None:
            print("Failed to retrieve Equity Daily Drawdown.")


def update_memory_DB():
    while True:
        time.sleep(0.2)
        global side1
        global side2
        global side3
        global dbTP1 
        global dbTP2
        global dbTP3
        global dbSL1 
        global dbSL2
        global dbSL3

        global ema_status


        # # Connect to the database
        conn = sqlite3.connect('memory_DB.sqlite', check_same_thread=False)

        # Create a cursor
        c1cc = conn.cursor()

        # Fetch the first row from memory_DB table
        c1cc.execute("SELECT side1, side2, side3, TP1, TP2, TP3, SL1, SL2, SL3 FROM memory_DB ORDER BY rowid ASC LIMIT 1")
        first_row_memory = c1cc.fetchone()

        # Fetch the first row from EMA_status table
        c1cc.execute("SELECT EMA FROM EMA_status ORDER BY rowid ASC LIMIT 1")
        first_row_ema_status = c1cc.fetchone()

        # Close the connection
        conn.close()

        # Unpack the results if they exist
        if first_row_memory:
            side1, side2, side3, dbTP1, dbTP2, dbTP3, dbSL1, dbSL2, dbSL3 = first_row_memory
        else:
            side1 = side2 = side3 = dbTP1 = dbTP2 = dbTP3 = dbSL1 = dbSL2 = dbSL3 = None

        ema_status = first_row_ema_status[0] if first_row_ema_status else None

        dbTP1 = float(dbTP1)
        dbTP2 = float(dbTP2)
        dbTP3 = float(dbTP3)

        dbSL1 = float(dbSL1)
        dbSL2 = float(dbSL2)
        dbSL3 = float(dbSL3)


        # ema_status = -1
        # time.sleep(5)
        # side1 = 0#1
        # side2 = 0#1
        # side3 = 0
        # dbTP1 = 0#53610.0
        # dbTP2 = 0#47700.0
        # dbTP3 = 0
        # dbSL2 = 0#44400.0
        # dbSL1 = 0#43300.0
        # dbSL3 = 0
        # time.sleep(15)

        # ema_status = -1
        # side1 = -1
        # side2 = -1
        # side3 = -1
        # dbTP1 = 60000
        # dbTP1 = float(dbTP1)
        # dbTP2 = 60000
        # dbTP2 = float(dbTP2)
        # dbTP3 = 60000
        # dbTP3 = float(dbTP3)
        # dbSL2 = 69000
        # dbSL2 = float(dbSL2)
        # dbSL1 = 68200
        # dbSL1 = float(dbSL1)
        # dbSL3 = 68000
        # dbSL3 = float(dbSL3)
        # time.sleep(80)







#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



def lot_sizes():
    while True:
        time.sleep(0.2)
        global live_price
        live_price =  mt5.symbol_info_tick(symbol).bid

        global spread_now
        spread_now = ((mt5.symbol_info_tick(symbol).ask - mt5.symbol_info_tick(symbol).bid) / mt5.symbol_info_tick(symbol).ask) * 100

        global time_active
        # Get the current time
        current_time = datetime.now()

        # Add two hours to the current time
        time_plus_two_hours = current_time + timedelta(hours=2)

        time_active = 0
        # Check if time_plus_two_hours is between 23:00 and 23:54 any day
        if time_plus_two_hours.hour == 23 and 0 <= time_plus_two_hours.minute <= 54:
            time_active = 1

          # Check if time_plus_two_hours is between 22:00 and 23:54 friday
        if current_time.weekday() == 4 and (time_plus_two_hours.hour == 22 or (time_plus_two_hours.hour == 23 and 0 <= time_plus_two_hours.minute <= 54)):
            time_active = 1

        global orders_can_be_placed
        # Check if it's Sunday and time is between 01:05 and 23:40
        if time_plus_two_hours.weekday() == 6 and (time_plus_two_hours.hour > 1 or (time_plus_two_hours.hour == 1 and time_plus_two_hours.minute >= 6)) and (time_plus_two_hours.hour < 23 or (time_plus_two_hours.hour == 23 and time_plus_two_hours.minute <= 40)):
            orders_can_be_placed = 1
        # Check if time is between 00:05 and 23:40 (for all other days) no sunday
        elif time_plus_two_hours.weekday() != 6 and (time_plus_two_hours.hour > 0 or (time_plus_two_hours.hour == 0 and time_plus_two_hours.minute >= 6)) and (time_plus_two_hours.hour < 23 or (time_plus_two_hours.hour == 23 and time_plus_two_hours.minute <= 40)):
            orders_can_be_placed = 1
        else:
            orders_can_be_placed = 0

            
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




#Function to insert equity data into the database
def insert_equity_data():
    global dd_daily_active
    global dd_percentage
    while True:
        time.sleep(10)
        # Get open positions
        positions = mt5.positions_get()

        # Check if there are no open positions
        if positions:
            # Connect to SQLite database for equity data
            conn = sqlite3.connect('equity_data.sqlite', detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()
            try:
                if max_drawdown > max_daily_dd_percentage:
                    dd_daily_active = 1
                else:
                    dd_daily_active = 0

                dd_percentage = max_drawdown

                account_info = mt5.account_info()
                if account_info:
                    equity = account_info.equity
                    timestamp = datetime.now().replace()  # Remove seconds and microseconds

                    # Insert equity data into the database
                    cursor.execute('''CREATE TABLE IF NOT EXISTS equity (
                                    timestamp TIMESTAMP PRIMARY KEY,
                                    equity FLOAT
                                )''')
                    cursor.execute("INSERT OR REPLACE INTO equity (timestamp, equity) VALUES (?, ?)", (timestamp, equity))
                    conn.commit()


                # Call the delete_old_data function to delete old data
                three_days_ago = datetime.now() - timedelta(days=3)
                try:
                    # Execute the DELETE query
                    cursor.execute("DELETE FROM equity WHERE timestamp < ?", (three_days_ago,))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    print('server over loaded?',{e})
                    time.sleep(10)
                    conn.close()
            except Exception as e:
                print('server over loaded?????',{e})
                time.sleep(10)
                conn.close()
        else:
            time.sleep(10)
            




#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





def account_inactive_trade():
    while True:
        global deals_in_history
        time.sleep(20)
        current_time = datetime.now()
        # Add two hours to the current time
        time_plus_two_hours = current_time + timedelta(hours=2)
        # Define the start and end dates for the last 10 days
        end_date = time_plus_two_hours
        start_date = end_date - timedelta(days=number_of_days_before_account_inactive)

        # get the number of deals in history for the last 10 days
        deals_in_history = mt5.history_deals_total(start_date, end_date)  # Pass dates as positional arguments
        if deals_in_history > 0:
            time.sleep(20)
            #print("Total deals in the last 10 days =", deals)
        else:
            print("No deals found in the last 10 days")

            try:
                def place_order(order_type, action):
                    symbol = 'BTCUSD'
                    live_price =  mt5.symbol_info_tick(symbol).ask
                    sl = live_price * 0.999
                    tp = live_price * 1.001

                    request = {
                        "action": action,
                        "symbol": symbol,
                        "volume": min_order_size_lot,
                        "type": order_type,
                        "sl": sl,
                        "tp": tp,
                        "deviation": 200,
                        "magic": 234000,
                        "comment": "no order placed in history",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_FOK,
                    }
                    return mt5.order_send(request)
                
                order = place_order(mt5.ORDER_TYPE_BUY, mt5.TRADE_ACTION_DEAL)
                if order is not None and 'Request executed' in order.comment:
                    print(f'no order placed in history so a trade was made so account isnt inactive: {order.order}') # , order ticket: {order["order"]}
                    time.sleep(1)
                else:
                    print(f'Order placement failed no order placed in history: ', order)
                    time.sleep(10)
            except Exception as e:
                print(f'An error occurred while placing no order placed in history: {e}')
                time.sleep(10)     


#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def risk_calculation():
    while True:
        time.sleep(0.5)
        global risk_total_global
        global total_risk_active
        def fetch_all_order_tickets():
            all_order_tickets = []

            # Function to fetch order ticket values from a specific database table
            def fetch_order_tickets(database_name, table_name):
                conn = sqlite3.connect(database_name)
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {table_name}_L")
                rows_L = cursor.fetchall()  # Fetch results for L
                cursor.execute(f"SELECT * FROM {table_name}_S")
                rows_S = cursor.fetchall()  # Fetch results for S
                conn.close()
                return rows_L + rows_S  # Concatenate the results

            # Define database names and corresponding table names
            databases = [
                ('tickets.sqlite', 'order_tickets_norm'),
                ('tickets_bbw.sqlite', 'order_tickets_bbw'),
                ('tickets_OI.sqlite', 'order_tickets_oi')
            ]

            # Fetch order tickets from each database and accumulate them
            for database_name, table_name in databases:
                order_tickets = fetch_order_tickets(database_name, table_name)
                all_order_tickets.extend(order_tickets)

            return all_order_tickets

        # Fetch all order ticket values from all databases
        all_order_tickets = fetch_all_order_tickets()

        total_risk_percentage = 0  # Initialize total risk percentage

        # Loop through each ticket in the order_tickets list
        for ticket_info in all_order_tickets:
            tickets = ticket_info[0]  # Extracting the ticket number
            try: 
                res = mt5.positions_get(ticket=tickets)
                if res is not None:
                    for position in res:
                        sl_price = position.sl  # Stop Loss price
                        volume_current = position.volume
                        price_open = position.price_open
                        if sl_price < price_open:
                            stop_loss_distance = price_open - sl_price
                        else:
                            stop_loss_distance = sl_price - price_open
                        risk_percentage = (stop_loss_distance * volume_current / account_balance) * 100
                        total_risk_percentage += risk_percentage  # Accumulate risk percentage
                        #print("Risk Percentage:", risk_percentage, "%")
            except Exception as e:
                print(f'An error occurred while updating RISK %: {e}')
                time.sleep(1)

        # Loop through each ticket in the order_tickets list (assuming these are pending orders)
        for ticket_info in all_order_tickets:
            tickets = ticket_info[0]  # Extracting the ticket number
            try: 
                get_orders = mt5.orders_get(ticket=tickets)
                if get_orders is not None:
                    for orders in get_orders:
                        sl_price = orders.sl  # Stop Loss price
                        volume_current = orders.volume_current
                        price_open = orders.price_open
                        if sl_price < price_open:
                            stop_loss_distance = price_open - sl_price
                        else:
                            stop_loss_distance = sl_price - price_open
                        risk_percentage = (stop_loss_distance * volume_current / account_balance) * 100
                        total_risk_percentage += risk_percentage  # Accumulate risk percentage
                        #print("Risk Percentage:", risk_percentage, "%")
            except Exception as e:
                print(f'An error occurred while updating RISK %: {e}')
                time.sleep(1)

        risk_total_global = total_risk_percentage
        if risk_total_global > input_risk_total_global:
            total_risk_active = 1
        else:
            total_risk_active = 0

        #print("Total Risk Percentage:", total_risk_percentage, "%")






#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



# def print_global_variables():
#     while True:
#         try:
#             data = [
#                 [f"\033[33mdbTP1\033[0m", f"\033[33m{dbTP1}\033[0m", f"\033[33mdbTP2\033[0m", f"\033[33m{dbTP2}\033[0m", f"\033[33mdbTP3\033[0m", f"\033[33m{dbTP3}\033[0m", f"\033[34mdd_daily_active\033[0m", f"\033[34m{dd_daily_active}\033[0m", f"\033[32mspread\033[0m", f"\033[32m{spread_now}\033[0m"],
#                 [f"\033[33mside1\033[0m", f"\033[33m{side1}\033[0m", f"\033[33mside2\033[0m", f"\033[33m{side2}\033[0m", f"\033[33mside3\033[0m", f"\033[33m{side3}\033[0m", f"\033[34mdd_percentage\033[0m", f"\033[34m{dd_percentage}\033[0m"],
#                 [f"\033[31mdbSL1\033[0m", f"\033[31m{dbSL1}\033[0m", f"\033[31mdbSL2\033[0m", f"\033[31m{dbSL2}\033[0m", f"\033[31mdbSL3\033[0m", f"\033[31m{dbSL3}\033[0m", f"\033[34mdeals_in_history\033[0m", f"\033[34m{deals_in_history}\033[0m"],
#                 [f"\033[31mnorm_active\033[0m", f"\033[31m{norm_active}\033[0m", f"\033[31mbbw_active\033[0m", f"\033[31m{bbw_active}\033[0m", f"\033[31moi_active\033[0m", f"\033[31m{oi_active}\033[0m", f"\033[34mdca_orders_short_oi\033[0m", f"\033[34m{dca_orders_short_oi}\033[0m", f"\033[34mrisk%\033[0m", f"\033[34m{risk_total_global}\033[0m"],
#                 [f"\033[31mema_status\033[0m", f"\033[31m{ema_status}\033[0m", f"\033[31mtime_active\033[0m", f"\033[31m{time_active}\033[0m", f"\033[31morders_can_be_placed\033[0m", f"\033[31m{orders_can_be_placed}\033[0m", f"\033[34mtotal_risk_active\033[0m", f"\033[34m{total_risk_active}\033[0m"],
#                 #[f"\033[34m" + "bank_1_exits" + "\033[0m", f"\033[34m{float(bank_1_exits)}\033[0m", f"\033[34m" + "order_1_bank" + "\033[0m", f"\033[34m{float(order_1_bank)}\033[0m"]
#             ]
#             table = tabulate(data, tablefmt="fancy_grid")
#             print(table)
#             time.sleep(4)
#         except Exception as e:
#             time.sleep(4)










#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------






# Function to place a pending order
def place_pending_order(order_type, action, price, lot, stop_loss, take_profit):
    symbol = 'BTCUSD'
    request = {
        "action": action,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": stop_loss,
        "tp": take_profit,
        "deviation": 20,
        "magic": 234000,
        "comment": "norm",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    return mt5.order_send(request)


# Main function
def norm_long():
    while True:
        global dca_orders
        global current_lot_size
        take_profit_price = dbTP1 # 10 pips
        stop_loss_price = dbSL1  # 40 pips
        # Connect to the SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect('memory_live_entries_DB.sqlite')
        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()
        # Update the value in the norm_active table
        cursor.execute("UPDATE norm_active SET norm_active = ?", (1,))
        conn.commit()
        conn.close()
        if dca_orders < max_dca_orders and total_risk_active==0: #and under deviation
            # Calculate new pending order price with a 0.2% decrease
            #initial_order_price = mt5.symbol_info_tick(symbol).bid
            new_order_price = initial_order_price * (1 - (deviation_percentage * dca_orders))
            truncated_price = round(new_order_price, 2)
            current_lot_size = math.floor(current_lot_size * 100) / 100 # round down 2 decimals

            if dca_orders == 0 and no_first_order == 1:
                dca_orders = dca_orders + 1
            else:
                try:
                    live_price =  mt5.symbol_info_tick(symbol).bid
                    if live_price < truncated_price:
                        truncated_price = live_price
                    order = place_pending_order(mt5.ORDER_TYPE_BUY_LIMIT, mt5.TRADE_ACTION_PENDING, truncated_price, current_lot_size, stop_loss_price, take_profit_price)
                    if order is not None and 'Request executed' in order.comment:
                        print(f'DCA Order placed successfully at price: {truncated_price}') # , order ticket: {order["order"]}
                        # Double the lot size for the next order

                        if no_first_order == 1:
                            current_lot_size = current_lot_size #* 2
                        else:
                            current_lot_size = current_lot_size * 2
                        dca_orders = dca_orders + 1

                        # Connect to SQLite database
                        conn = sqlite3.connect('tickets.sqlite')
                        cursor = conn.cursor()
                        # Create table if it doesn't exist
                        cursor.execute('''CREATE TABLE IF NOT EXISTS order_tickets_norm_L (
                                            order_tickets_norm_L INTEGER
                                        )''')
                        # Function to insert order ticket into the database
                        def insert_order_ticket(order_tickets_norm_L):
                            cursor.execute("INSERT INTO order_tickets_norm_L (order_tickets_norm_L) VALUES (?)", (order_tickets_norm_L,))
                            conn.commit()
                            print("Order ticket inserted successfully.")
                        insert_order_ticket(order.order)
                        conn.close()
                        time.sleep(5)

                    else:
                        print(f'Order placement failed:   lot size: {current_lot_size}  ', order)
                        time.sleep(1)
                        dca_orders = dca_orders + 1
                except Exception as e:
                    print(f'An error occurred while placing the DCA order: {e}')
                    time.sleep(1)
                    dca_orders = dca_orders + 1
        else:
            print(f"All DCA orders placed. Total orders: {dca_orders}")
            break  # Exit the loop if the maximum number of orders is reached



def norm_short():
    while True:
        global dca_orders_short
        global current_lot_size_short
        take_profit_price_short = dbTP1  # 10 pips
        stop_loss_price_short = dbSL1  # 40 pips

        # Connect to the SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect('memory_live_entries_DB.sqlite')
        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()
        # Update the value in the norm_active table
        cursor.execute("UPDATE norm_active SET norm_active = ?", (1,))
        conn.commit()
        conn.close()

        if dca_orders_short < max_dca_orders_short and total_risk_active==0: #and under deviation
            #initial_order_price_short = mt5.symbol_info_tick(symbol).ask
            new_order_price = initial_order_price_short * (1 + (deviation_percentage_short * dca_orders_short))
            truncated_price = round(new_order_price, 2)
            current_lot_size_short = math.floor(current_lot_size_short * 100) / 100 # round down 2 decimals

            if dca_orders_short == 0 and no_first_order == 1:
                dca_orders_short = dca_orders_short + 1
            else:
                try:
                    live_price =  mt5.symbol_info_tick(symbol).ask
                    if live_price > truncated_price:
                        truncated_price = live_price
                    # Place pending order
                    order = place_pending_order(mt5.ORDER_TYPE_SELL_LIMIT, mt5.TRADE_ACTION_PENDING, truncated_price, current_lot_size_short, stop_loss_price_short, take_profit_price_short)
                    if order is not None and 'Request executed' in order.comment:
                        print(f'DCA Order placed successfully at price: {truncated_price}, lot size: {current_lot_size_short}') # , order ticket: {order["order"]}
                        dca_orders_short = dca_orders_short + 1
                        # Double the lot size for the next order
                        if no_first_order == 1:
                            current_lot_size_short = current_lot_size_short #* 2
                        else:
                            current_lot_size_short = current_lot_size_short * 2

                        # Connect to SQLite database
                        conn = sqlite3.connect('tickets.sqlite')
                        cursor = conn.cursor()
                        # Create table if it doesn't exist
                        cursor.execute('''CREATE TABLE IF NOT EXISTS order_tickets_norm_S (
                                            order_tickets_norm_S INTEGER
                                        )''')
                        # Function to insert order ticket into the database
                        def insert_order_ticket(order_tickets_norm_S):
                            cursor.execute("INSERT INTO order_tickets_norm_S (order_tickets_norm_S) VALUES (?)", (order_tickets_norm_S,))
                            conn.commit()
                            print("Order ticket inserted successfully.")
                        insert_order_ticket(order.order)
                        conn.close()
                        time.sleep(5)

                    else:
                        print(f'Order placement failed:   lot size: {current_lot_size_short}  ', order)
                        time.sleep(1)
                        dca_orders_short = dca_orders_short + 1
                except Exception as e:
                    print(f'An error occurred while placing the DCA order: {e}')
                    time.sleep(1)
                    dca_orders_short = dca_orders_short + 1
        else:
            print(f"All DCA orders placed. Total orders: {dca_orders_short}")
            break  # Exit the loop if the maximum number of orders is reached






def norm_orders():
    while True:
        time.sleep(1)
        if norm_active == 0 and time_active == 0 and live_price < (dbTP1 * (1-time_open_threshhold_norm)) and orders_can_be_placed == 1 and dd_daily_active == 0 and total_risk_active==0:
            if dbTP1 != 0 and dca_orders==0 and side1 == 1: #< max_dca_orders
                
                # Connect to the SQLite database (or create it if it doesn't exist)
                conn = sqlite3.connect('memory_live_entries_DB.sqlite')
                # Create a cursor object to execute SQL queries
                cursor = conn.cursor()
                # Update the value in the norm_active table
                cursor.execute("UPDATE norm_active SET norm_active = ?", (1,))
                conn.commit()
                conn.close()
                global initial_order_price
                initial_order_price = mt5.symbol_info_tick(symbol).bid

                global current_lot_size
                initial_lot_size = order_size_norm / live_price 
                current_lot_size = initial_lot_size
                #current_lot_size = round(current_lot_size, 2)
                current_lot_size = math.floor(current_lot_size * 100) / 100 # round down 2 decimals
                # Run norm_long() function in a separate thread
                long_thread = threading.Thread(target=norm_long)
                long_thread.start()
                # Wait for norm_long() to finish
                long_thread.join()

        if norm_active == 0 and time_active == 0 and live_price > (dbTP1 * (1+time_open_threshhold_norm)) and orders_can_be_placed == 1 and dd_daily_active == 0 and total_risk_active==0:
            if dbTP1 != 0 and dca_orders_short==0 and side1 == -1: 

                # Connect to the SQLite database (or create it if it doesn't exist)
                conn = sqlite3.connect('memory_live_entries_DB.sqlite')
                # Create a cursor object to execute SQL queries
                cursor = conn.cursor()
                # Update the value in the norm_active table
                cursor.execute("UPDATE norm_active SET norm_active = ?", (1,))
                conn.commit()
                conn.close()
                global initial_order_price_short
                initial_order_price_short = mt5.symbol_info_tick(symbol).ask

                global current_lot_size_short
                initial_lot_size_short = order_size_norm / live_price 
                current_lot_size_short = initial_lot_size_short
                ###current_lot_size_short = round(current_lot_size_short, 2)
                current_lot_size_short = math.floor(current_lot_size_short * 100) / 100 # round down 2 decimals
                # Run norm_short() function in a separate thread
                short_thread = threading.Thread(target=norm_short)
                short_thread.start()
                # Wait for norm_short() to finish
                short_thread.join()




def norm_update():
    while True:
        time.sleep(5)

        # Connect to SQLite database
        conn = sqlite3.connect('tickets.sqlite')
        cursor = conn.cursor()

        # Function to fetch all order ticket values from the database
        def fetch_order_tickets():
            cursor.execute("SELECT * FROM order_tickets_norm_L")
            rows = cursor.fetchall()
            return rows

        # Fetch all order ticket values
        order_tickets = fetch_order_tickets()
        conn.close()

        # Loop through each ticket in the order_tickets list
        for ticket_info in order_tickets:
            tickets = ticket_info[0]  # Extracting the ticket number

            try:
                res = mt5.positions_get(ticket=tickets)
                if res is not None:
                    for position in res:
                        # Access the tp attribute for each position object
                        tp_value = position.tp
                        ticket = position.identifier
                        #print(f"open ticket {tickets} {tp_value} ")
                        if tp_value != dbTP1 and side1 == 1:
                            try:
                                # Update SL and TP for filled orders
                                request = {
                                    'action': mt5.TRADE_ACTION_SLTP,
                                    'position': ticket,
                                    'sl': dbSL1,
                                    'tp': dbTP1
                                }
                                ress = mt5.order_send(request)
                                if ress is not None and 'Request executed' in ress.comment:
                                    print(f"SL and TP updated successfully for order {ticket}")
                                else:
                                    print(f"cant update {ticket} {ress}")
                            except Exception as e:
                                print(f"error exception! {ticket} {e}")
                                time.sleep(5)
            except Exception as e:
                print(f"error exception! {ticket} {e}")
                time.sleep(5)

        # Connect to SQLite database
        conn = sqlite3.connect('tickets.sqlite')
        cursor = conn.cursor()

                # Function to fetch all order ticket values from the database
        def fetch_order_tickets():
            cursor.execute("SELECT * FROM order_tickets_norm_S")
            rows = cursor.fetchall()
            return rows

        # Fetch all order ticket values
        order_tickets = fetch_order_tickets()
        conn.close()

        # Loop through each ticket in the order_tickets list
        for ticket_info in order_tickets:
            tickets = ticket_info[0]  # Extracting the ticket number

            try:
                res = mt5.positions_get(ticket=tickets)
                if res is not None:
                    for position in res:
                        # Access the tp attribute for each position object
                        tp_value = position.tp
                        ticket = position.identifier
                        #print(f"open ticket {tickets} {tp_value} ")
                        if tp_value != dbTP1 and side1 == -1:
                            try:
                                # Update SL and TP for filled orders
                                request = {
                                    'action': mt5.TRADE_ACTION_SLTP,
                                    'position': ticket,
                                    'sl': dbSL1,
                                    'tp': dbTP1
                                }
                                ress = mt5.order_send(request)
                                if ress is not None and 'Request executed' in ress.comment:
                                    print(f"SL and TP updated successfully for order {ticket}")
                                else:
                                    print(f"cant update {ticket} {ress}")
                            except Exception as e:
                                print(f"error exception! {ticket} {e}")
                                time.sleep(5)
            except Exception as e:
                print(f"error exception! {ticket} {e}")
                time.sleep(5)



def close_all_norm():
    time.sleep(1)
    while True:
        if time_active == 1 and side1 == 1 and live_price > (dbTP1 * (1-time_close_threshhold)):
            close_all_true = 1
            print('closing trade before SWAP FEE')
        else:
            close_all_true = 0
        if time_active == 1 and side1 == -1 and live_price < (dbTP1 * (1+time_close_threshhold)):
            close_all_true = 1
            print('closing trade before SWAP FEE')
        else:
            close_all_true = 0

        if dbTP1 == 0 and norm_active != 0 or close_all_true == 1 or norm_needs_reset == 1:
            time.sleep(0.1)
            # Connect to SQLite database
            conn = sqlite3.connect('tickets.sqlite')
            cursor = conn.cursor()

            # Function to fetch all order ticket values from the database
            def fetch_order_tickets():
                cursor.execute("SELECT * FROM order_tickets_norm_L")
                rows = cursor.fetchall()
                return rows

            # Fetch all order ticket values
            order_tickets = fetch_order_tickets()
            conn.close()
            # Loop through each ticket in the order_tickets list
            for ticket_info in order_tickets:
                ticket = ticket_info[0]  # Extracting the ticket number
                try:
                    request = {
                            'action': mt5.TRADE_ACTION_REMOVE,  # Use TRADE_ACTION_REMOVE to close the order
                            'order': ticket,  # Specify the ticket number of the order to close
                        }

                    # Send the order removal request
                    result = mt5.order_send(request)
                    
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"yay {ticket}")
                        # Delete the ticket from the database
                        conn = sqlite3.connect('tickets.sqlite')
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM order_tickets_norm_L WHERE order_tickets_norm_L = ?", (ticket,))
                        conn.commit()
                        conn.close()
                    else:
                        print(f"ORDER with ticket {ticket} not found.")
                        # print(f"cshit {ticket} {ticket} ")
                        # if result is not None and 'Invalid request' in result.comment:
                        #     conn = sqlite3.connect('tickets.sqlite')
                        #     cursor = conn.cursor()
                        #     cursor.execute("DELETE FROM order_tickets_norm_L WHERE order_tickets_norm_L = ?", (ticket,))
                        #     conn.commit()
                        #     conn.close()
                except Exception as e:
                    print(f"errorrr {ticket} {e}")
                    time.sleep(0.1)
                    #print(f"Error: {str(e)}")


            # Loop through each order ticket
            for ticket_info in order_tickets:
                ticket = ticket_info[0]  # Extracting the ticket number
                try:
                    position_tuple = mt5.positions_get(ticket=ticket)
                    if position_tuple is None or len(position_tuple) == 0:
                        print(f"Position with ticket {ticket} not found. {position_tuple}")
                        result_po = mt5.history_deals_get(position=ticket)
                        if result_po is not None:
                            print(f"ticket {ticket} deleted")
                            conn = sqlite3.connect('tickets.sqlite')
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM order_tickets_norm_L WHERE order_tickets_norm_L = ?", (ticket,))
                            conn.commit()
                            conn.close()
                    else:
                        position = position_tuple[0] 
                        volume = position.volume
                        print(f"Volume of position {ticket}: {position}")

                        request = {
                            'action': mt5.TRADE_ACTION_DEAL,
                            'position': ticket,
                            'symbol': symbol,
                            'type': mt5.DEAL_TYPE_SELL,
                            'volume': volume,                        
                            'deviation': 20,
                            'magic': 234001,
                            
                        }
                        result = mt5.order_send(request)
                        if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
                            print(f"Position {ticket} closed successfully")
                            # Delete the ticket from the database
                            conn = sqlite3.connect('tickets.sqlite')
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM order_tickets_norm_L WHERE order_tickets_norm_L = ?", (ticket,))
                            conn.commit()
                            conn.close()
                        else:
                            print(f"Failed to close position {ticket}: {result}")
                            conn = sqlite3.connect('tickets.sqlite')
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM order_tickets_norm_L WHERE order_tickets_norm_L = ?", (ticket,))
                            conn.commit()
                            conn.close()
                except Exception as e:
                    print(f"errorrr {ticket} {e}")
                    time.sleep(0.1)
                    # Handle the exception
            

            # Connect to SQLite database
            conn = sqlite3.connect('tickets.sqlite')
            cursor = conn.cursor()

            # Function to fetch all order ticket values from the database
            def fetch_order_tickets():
                cursor.execute("SELECT * FROM order_tickets_norm_S")
                rows = cursor.fetchall()
                return rows

            # Fetch all order ticket values
            order_tickets = fetch_order_tickets()
            conn.close()
            # Loop through each ticket in the order_tickets list
            for ticket_info in order_tickets:
                ticket = ticket_info[0]  # Extracting the ticket number
                try:
                    request = {
                            'action': mt5.TRADE_ACTION_REMOVE,  # Use TRADE_ACTION_REMOVE to close the order
                            'order': ticket,  # Specify the ticket number of the order to close
                        }

                    # Send the order removal request
                    result = mt5.order_send(request)
                    
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"yay {ticket}")
                        # Delete the ticket from the database
                        conn = sqlite3.connect('tickets.sqlite')
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM order_tickets_norm_S WHERE order_tickets_norm_S = ?", (ticket,))
                        conn.commit()
                        conn.close()
                    else:
                        print(f"ORDER with ticket {ticket} not found.")
                        # print(f"cshit {ticket} {ticket} ")
                        # if result is not None and 'Invalid request' in result.comment:
                        #     conn = sqlite3.connect('tickets.sqlite')
                        #     cursor = conn.cursor()
                        #     cursor.execute("DELETE FROM order_tickets_norm_S WHERE order_tickets_norm_S = ?", (ticket,))
                        #     conn.commit()
                        #     conn.close()
                except Exception as e:
                    print(f"errorrr {ticket} {e}")
                    time.sleep(0.1)
                    #print(f"Error: {str(e)}")


            # Loop through each order ticket
            for ticket_info in order_tickets:
                ticket = ticket_info[0]  # Extracting the ticket number
                try:
                    position_tuple = mt5.positions_get(ticket=ticket)
                    if position_tuple is None or len(position_tuple) == 0:
                        print(f"Position with ticket {ticket} not found.  ")
                        result_po = mt5.history_deals_get(position=ticket)
                        if result_po is not None:
                            print(f"ticket {ticket} deleted")
                            conn = sqlite3.connect('tickets.sqlite')
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM order_tickets_norm_S WHERE order_tickets_norm_S = ?", (ticket,))
                            conn.commit()
                            conn.close()
                    else:
                        position = position_tuple[0] 
                        volume = position.volume
                        print(f"Volume of position {ticket}: {position}")

                        request = {
                            'action': mt5.TRADE_ACTION_DEAL,
                            'position': ticket,
                            'symbol': symbol,
                            'type': mt5.DEAL_TYPE_BUY,
                            'volume': volume,                        
                            'deviation': 20,
                            'magic': 234002,
                            
                        }
                        result = mt5.order_send(request)
                        if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
                            print(f"Position {ticket} closed successfully")
                            # Delete the ticket from the database
                            conn = sqlite3.connect('tickets.sqlite')
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM order_tickets_norm_S WHERE order_tickets_norm_S = ?", (ticket,))
                            conn.commit()
                            conn.close()
                        else:
                            print(f"Failed to close position {ticket}: {result}")
                            # conn = sqlite3.connect('tickets.sqlite')
                            # cursor = conn.cursor()
                            # cursor.execute("DELETE FROM order_tickets_norm_S WHERE order_tickets_norm_S = ?", (ticket,))
                            # conn.commit()
                            # conn.close()
                except Exception as e:
                    print(f"errorrr {ticket} {e}")
                    time.sleep(0.1)
                    # Handle the exception

            global dca_orders_short
            global dca_orders
            dca_orders_short = 0
            dca_orders = 0

            global current_lot_size
            global current_lot_size_short
            current_lot_size = initial_lot_size
            current_lot_size_short = initial_lot_size_short

            # Connect to the SQLite database (or create it if it doesn't exist)
            conn = sqlite3.connect('memory_live_entries_DB.sqlite')
            # Create a cursor object to execute SQL queries
            cursor = conn.cursor()
            # Update the value in the norm_active table
            cursor.execute("UPDATE norm_active SET norm_active = ?", (0,))
            conn.commit()
            conn.close()

        else:
            time.sleep(1)





#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------






# Function to place a pending order
def place_pending_order_bbw(order_type, action, price, lot, stop_loss, take_profit):
    symbol = 'BTCUSD'
    request = {
        "action": action,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": stop_loss,
        "tp": take_profit,
        "deviation": 20,
        "magic": 234000,
        "comment": "bbw",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    return mt5.order_send(request)


# Main function
def bbw_long():
    while True:
        global dca_orders_bbw
        global current_lot_size_bbw
        take_profit_price_bbw = dbTP2  # 10 pips
        stop_loss_price_bbw = dbSL2  # 40 pips
        # Connect to the SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect('memory_live_entries_DB.sqlite')
        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()
        # Update the value in the bbw_active table
        cursor.execute("UPDATE bbw_active SET bbw_active = ?", (1,))
        conn.commit()
        conn.close()

        if dca_orders_bbw < max_dca_orders_bbw and total_risk_active==0: #and under deviation
            # Calculate new pending order price with a 0.2% decrease
            #initial_order_price_bbw = mt5.symbol_info_tick(symbol).bid
            new_order_price = initial_order_price_bbw * (1 - (deviation_percentage_bbw * dca_orders_bbw))
            truncated_price = round(new_order_price, 2)
            current_lot_size_bbw = math.floor(current_lot_size_bbw * 100) / 100 # round down 2 decimals

            try:
                # Place pending order
                live_price =  mt5.symbol_info_tick(symbol).bid
                if live_price < truncated_price:
                    truncated_price = live_price
                order = place_pending_order_bbw(mt5.ORDER_TYPE_BUY_LIMIT, mt5.TRADE_ACTION_PENDING, truncated_price, current_lot_size_bbw, stop_loss_price_bbw, take_profit_price_bbw)
                if order is not None and 'Request executed' in order.comment:
                    print(f'DCA Order placed successfully at price: {truncated_price}, lot size: {current_lot_size_bbw}') # , order ticket: {order["order"]}
                    dca_orders_bbw = dca_orders_bbw + 1
                    # Double the lot size for the next order
                    #current_lot_size_bbw = current_lot_size_bbw * 2

                    # Connect to SQLite database
                    conn = sqlite3.connect('tickets_bbw.sqlite')
                    cursor = conn.cursor()
                    # Create table if it doesn't exist
                    cursor.execute('''CREATE TABLE IF NOT EXISTS order_tickets_bbw_L (
                                        order_tickets_bbw_L INTEGER
                                    )''')
                    # Function to insert order ticket into the database
                    def insert_order_ticket(order_tickets_bbw_L):
                        cursor.execute("INSERT INTO order_tickets_bbw_L (order_tickets_bbw_L) VALUES (?)", (order_tickets_bbw_L,))
                        conn.commit()
                        print("Order ticket inserted successfully.")
                    insert_order_ticket(order.order)
                    conn.close()
                    time.sleep(5)


                else:
                    print(f'Order placement failed:   lot size: {current_lot_size_bbw}  ', order)
                    time.sleep(1)
                    dca_orders_bbw = dca_orders_bbw + 1
            except Exception as e:
                print(f'An error occurred while placing the DCA order: {e}')
                time.sleep(1)
                dca_orders_bbw = dca_orders_bbw + 1
        else:
            print(f"All DCA orders placed. Total orders: {dca_orders_bbw}")
            break  # Exit the loop if the maximum number of orders is reached



def short_bbw():
    while True:
        global dca_orders_short_bbw
        global current_lot_size_short_bbw
        take_profit_price_short_bbw = dbTP2  # 10 pips
        stop_loss_price_short_bbw = dbSL2  # 40 pips

        # Connect to the SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect('memory_live_entries_DB.sqlite')
        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()
        # Update the value in the bbw_active table
        cursor.execute("UPDATE bbw_active SET bbw_active = ?", (1,))
        conn.commit()
        conn.close()

        if dca_orders_short_bbw < max_dca_orders_short_bbw and total_risk_active==0: #and under deviation
            #initial_order_price_short_bbw = mt5.symbol_info_tick(symbol).ask
            new_order_price = initial_order_price_short_bbw * (1 + (deviation_percentage_short_bbw * dca_orders_short_bbw))
            truncated_price = round(new_order_price, 2)
            current_lot_size_short_bbw = math.floor(current_lot_size_short_bbw * 100) / 100 # round down 2 decimals

            try:                
                live_price =  mt5.symbol_info_tick(symbol).ask
                if live_price > truncated_price:
                    truncated_price = live_price
                # Place pending order
                order = place_pending_order_bbw(mt5.ORDER_TYPE_SELL_LIMIT, mt5.TRADE_ACTION_PENDING, truncated_price, current_lot_size_short_bbw, stop_loss_price_short_bbw, take_profit_price_short_bbw)
                if order is not None and 'Request executed' in order.comment:
                    print(f'DCA Order placed successfully at price: {truncated_price}, lot size: {current_lot_size_short_bbw}') # , order ticket: {order["order"]}
                    dca_orders_short_bbw = dca_orders_short_bbw + 1
                    # Double the lot size for the next order
                    #current_lot_size_short_bbw = current_lot_size_short_bbw * 2

                    # Connect to SQLite database
                    conn = sqlite3.connect('tickets_bbw.sqlite')
                    cursor = conn.cursor()
                    # Create table if it doesn't exist
                    cursor.execute('''CREATE TABLE IF NOT EXISTS order_tickets_bbw_S (
                                        order_tickets_bbw_S INTEGER
                                    )''')
                    # Function to insert order ticket into the database
                    def insert_order_ticket(order_tickets_bbw_S):
                        cursor.execute("INSERT INTO order_tickets_bbw_S (order_tickets_bbw_S) VALUES (?)", (order_tickets_bbw_S,))
                        conn.commit()
                        print("Order ticket inserted successfully.")
                    insert_order_ticket(order.order)
                    conn.close()
                    time.sleep(5)
                else:
                    print(f'Order placement failed:   lot size: {current_lot_size_short_bbw}  ', order)
                    time.sleep(1)
                    dca_orders_short_bbw = dca_orders_short_bbw + 1
            except Exception as e:
                print(f'An error occurred while placing the DCA order: {e}')
                time.sleep(1)
                dca_orders_short_bbw = dca_orders_short_bbw + 1
        else:
            print(f"All DCA orders placed. Total orders: {dca_orders_short_bbw}")
            break  # Exit the loop if the maximum number of orders is reached





def orders_bbw():
    while True:
        time.sleep(1)
        if bbw_active == 0 and time_active == 0 and live_price < (dbTP2 * (1-time_open_threshhold_bbw)) and orders_can_be_placed == 1 and dd_daily_active == 0 and total_risk_active==0:
            if dbTP2 != 0 and dca_orders_bbw==0 and side2 == 1:

                # Connect to the SQLite database (or create it if it doesn't exist)
                conn = sqlite3.connect('memory_live_entries_DB.sqlite')
                # Create a cursor object to execute SQL queries
                cursor = conn.cursor()
                # Update the value in the bbw_active table
                cursor.execute("UPDATE bbw_active SET bbw_active = ?", (1,))
                conn.commit()
                conn.close()
                global initial_order_price_bbw
                initial_order_price_bbw = mt5.symbol_info_tick(symbol).bid

                global current_lot_size_bbw
                initial_lot_size_bbw = order_size_bbw / live_price 
                current_lot_size_bbw = initial_lot_size_bbw
                #current_lot_size_bbw = round(current_lot_size_bbw, 2)
                current_lot_size_bbw = math.floor(current_lot_size_bbw * 100) / 100 # round down 2 decimals
                # Run bbw_long() function in a separate thread
                long_thread = threading.Thread(target=bbw_long)
                long_thread.start()
                # Wait for bbw_long() to finish
                long_thread.join()

        if bbw_active == 0 and time_active == 0 and live_price > (dbTP2 * (1+time_open_threshhold_bbw)) and orders_can_be_placed == 1 and dd_daily_active == 0 and total_risk_active==0:
            if dbTP2 != 0 and dca_orders_short_bbw==0 and side2 == -1:

                # Connect to the SQLite database (or create it if it doesn't exist)
                conn = sqlite3.connect('memory_live_entries_DB.sqlite')
                # Create a cursor object to execute SQL queries
                cursor = conn.cursor()
                # Update the value in the bbw_active table
                cursor.execute("UPDATE bbw_active SET bbw_active = ?", (1,))
                conn.commit()
                conn.close()
                global initial_order_price_short_bbw
                initial_order_price_short_bbw = mt5.symbol_info_tick(symbol).ask

                global current_lot_size_short_bbw
                initial_lot_size_short_bbw = order_size_bbw / live_price 
                current_lot_size_short_bbw = initial_lot_size_short_bbw
                #current_lot_size_short_bbw = round(current_lot_size_short_bbw, 2)
                current_lot_size_short_bbw = math.floor(current_lot_size_short_bbw * 100) / 100 # round down 2 decimals
                # Run short_bbw() function in a separate thread
                short_thread = threading.Thread(target=short_bbw)
                short_thread.start()
                # Wait for short_bbw() to finish
                short_thread.join()




def update_bbw():
    while True:
        time.sleep(5)

        # Connect to SQLite database
        conn = sqlite3.connect('tickets_bbw.sqlite')
        cursor = conn.cursor()

        # Function to fetch all order ticket values from the database
        def fetch_order_tickets():
            cursor.execute("SELECT * FROM order_tickets_bbw_L")
            rows = cursor.fetchall()
            return rows

        # Fetch all order ticket values
        order_tickets = fetch_order_tickets()
        conn.close()

        # Loop through each ticket in the order_tickets list
        for ticket_info in order_tickets:
            tickets = ticket_info[0]  # Extracting the ticket number

            try:
                res = mt5.positions_get(ticket=tickets)
                if res is not None:
                    for position in res:
                        # Access the tp attribute for each position object
                        tp_value = position.tp
                        ticket = position.identifier
                        #print(f"open ticket {tickets} {tp_value} ")
                        if tp_value != dbTP2 and side2 == 1:
                            try:
                                # Update SL and TP for filled orders
                                request = {
                                    'action': mt5.TRADE_ACTION_SLTP,
                                    'position': ticket,
                                    'sl': dbSL2,
                                    'tp': dbTP2
                                }
                                ress = mt5.order_send(request)
                                if ress is not None and 'Request executed' in ress.comment:
                                    print(f"SL and TP updated successfully for order {ticket}")
                                else:
                                    print(f"cant update {ticket} {ress}")
                            except Exception as e:
                                print(f"error exception! {ticket} {e}")
                                time.sleep(5)
            except Exception as e:
                print(f"error exception! {ticket} {e}")
                time.sleep(5)

        # Connect to SQLite database
        conn = sqlite3.connect('tickets_bbw.sqlite')
        cursor = conn.cursor()

                # Function to fetch all order ticket values from the database
        def fetch_order_tickets():
            cursor.execute("SELECT * FROM order_tickets_bbw_S")
            rows = cursor.fetchall()
            return rows

        # Fetch all order ticket values
        order_tickets = fetch_order_tickets()
        conn.close()

        # Loop through each ticket in the order_tickets list
        for ticket_info in order_tickets:
            tickets = ticket_info[0]  # Extracting the ticket number

            try:
                res = mt5.positions_get(ticket=tickets)
                if res is not None:
                    for position in res:
                        # Access the tp attribute for each position object
                        tp_value = position.tp
                        ticket = position.identifier
                        #print(f"open ticket {tickets} {tp_value} ")
                        if tp_value != dbTP2 and side2 == -1:
                            try:
                                # Update SL and TP for filled orders
                                request = {
                                    'action': mt5.TRADE_ACTION_SLTP,
                                    'position': ticket,
                                    'sl': dbSL2,
                                    'tp': dbTP2
                                }
                                ress = mt5.order_send(request)
                                if ress is not None and 'Request executed' in ress.comment:
                                    print(f"SL and TP updated successfully for order {ticket}")
                                else:
                                    print(f"cant update {ticket} {ress}")
                            except Exception as e:
                                print(f"error exception! {ticket} {e}")
                                time.sleep(5)
            except Exception as e:
                print(f"error exception! {ticket} {e}")
                time.sleep(5)





def close_all_bbw():
    time.sleep(1)
    while True:
        if time_active == 1 and side2 == 1 and live_price > (dbTP2 * (1-time_close_threshhold)):
            close_all_true = 1
            print('closing trade before SWAP FEE')
        else:
            close_all_true = 0
        if time_active == 1 and side2 == -1 and live_price < (dbTP2 * (1+time_close_threshhold)):
            close_all_true = 1
            print('closing trade before SWAP FEE')
        else:
            close_all_true = 0
        if dbTP2 == 0 and bbw_active != 0 or close_all_true == 1 or bbw_needs_reset == 1:
            time.sleep(0.1)
            # Connect to SQLite database
            conn = sqlite3.connect('tickets_bbw.sqlite')
            cursor = conn.cursor()

            # Function to fetch all order ticket values from the database
            def fetch_order_tickets():
                cursor.execute("SELECT * FROM order_tickets_bbw_L")
                rows = cursor.fetchall()
                return rows

            # Fetch all order ticket values
            order_tickets = fetch_order_tickets()
            conn.close()
            # Loop through each ticket in the order_tickets list
            for ticket_info in order_tickets:
                ticket = ticket_info[0]  # Extracting the ticket number
                try:
                    request = {
                            'action': mt5.TRADE_ACTION_REMOVE,  # Use TRADE_ACTION_REMOVE to close the order
                            'order': ticket,  # Specify the ticket number of the order to close
                        }

                    # Send the order removal request
                    result = mt5.order_send(request)
                    
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"yay {ticket}")
                        # Delete the ticket from the database
                        conn = sqlite3.connect('tickets_bbw.sqlite')
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM order_tickets_bbw_L WHERE order_tickets_bbw_L = ?", (ticket,))
                        conn.commit()
                        conn.close()
                    else:
                        print(f"ORDER with ticket {ticket} not found.")
                        # print(f"cshit {ticket} {result} ")
                        # if result is not None and 'Invalid request' in result.comment:
                        #     conn = sqlite3.connect('tickets_bbw.sqlite')
                        #     cursor = conn.cursor()
                        #     cursor.execute("DELETE FROM order_tickets_bbw_L WHERE order_tickets_bbw_L = ?", (ticket,))
                        #     conn.commit()
                        #     conn.close()
                except Exception as e:
                    print(f"errorrr {ticket} {e}")
                    time.sleep(0.1)
                    #print(f"Error: {str(e)}")


            # Loop through each order ticket
            for ticket_info in order_tickets:
                ticket = ticket_info[0]  # Extracting the ticket number
                try:
                    position_tuple = mt5.positions_get(ticket=ticket)
                    if position_tuple is None or len(position_tuple) == 0:
                        print(f"Position with ticket {ticket} not found.")
                        result_po = mt5.history_deals_get(position=ticket)
                        if result_po is not None:
                            print(f"ticket {ticket} deleted")
                            conn = sqlite3.connect('tickets_bbw.sqlite')
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM order_tickets_bbw_L WHERE order_tickets_bbw_L = ?", (ticket,))
                            conn.commit()
                            conn.close()
                    else:
                        position = position_tuple[0] 
                        volume = position.volume
                        print(f"Volume of position {ticket}: {position}")

                        request = {
                            'action': mt5.TRADE_ACTION_DEAL,
                            'position': ticket,
                            'symbol': symbol,
                            'type': mt5.DEAL_TYPE_SELL,
                            'volume': volume,                        
                            'deviation': 20,
                            'magic': 234001,
                            
                        }
                        result = mt5.order_send(request)
                        if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
                            print(f"Position {ticket} closed successfully")
                            # Delete the ticket from the database
                            conn = sqlite3.connect('tickets_bbw.sqlite')
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM order_tickets_bbw_L WHERE order_tickets_bbw_L = ?", (ticket,))
                            conn.commit()
                            conn.close()
                        else:
                            print(f"Failed to close position {ticket}: {result}")
                            # conn = sqlite3.connect('tickets_bbw.sqlite')
                            # cursor = conn.cursor()
                            # cursor.execute("DELETE FROM order_tickets_bbw_L WHERE order_tickets_bbw_L = ?", (ticket,))
                            # conn.commit()
                            # conn.close()
                except Exception as e:
                    print(f"errorrr {ticket} {e} {result}")
                    time.sleep(0.1)
                    # Handle the exception
            

            # Connect to SQLite database
            conn = sqlite3.connect('tickets_bbw.sqlite')
            cursor = conn.cursor()

            # Function to fetch all order ticket values from the database
            def fetch_order_tickets():
                cursor.execute("SELECT * FROM order_tickets_bbw_S")
                rows = cursor.fetchall()
                return rows

            # Fetch all order ticket values
            order_tickets = fetch_order_tickets()
            conn.close()
            # Loop through each ticket in the order_tickets list
            for ticket_info in order_tickets:
                ticket = ticket_info[0]  # Extracting the ticket number
                try:
                    request = {
                            'action': mt5.TRADE_ACTION_REMOVE,  # Use TRADE_ACTION_REMOVE to close the order
                            'order': ticket,  # Specify the ticket number of the order to close
                        }

                    # Send the order removal request
                    result = mt5.order_send(request)
                    
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"yay {ticket}")
                        # Delete the ticket from the database
                        conn = sqlite3.connect('tickets_bbw.sqlite')
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM order_tickets_bbw_S WHERE order_tickets_bbw_S = ?", (ticket,))
                        conn.commit()
                        conn.close()
                    else:
                        print(f"ORDER with ticket {ticket} not found.")
                        # print(f"cshit {ticket} {result} ")
                        # if result is not None and 'Invalid request' in result.comment:
                        #     conn = sqlite3.connect('tickets_bbw.sqlite')
                        #     cursor = conn.cursor()
                        #     cursor.execute("DELETE FROM order_tickets_bbw_S WHERE order_tickets_bbw_S = ?", (ticket,))
                        #     conn.commit()
                        #     conn.close()
                except Exception as e:
                    print(f"errorrr {ticket} {e} {result}")
                    time.sleep(0.1)
                    #print(f"Error: {str(e)}")


            # Loop through each order ticket
            for ticket_info in order_tickets:
                ticket = ticket_info[0]  # Extracting the ticket number
                try:
                    position_tuple = mt5.positions_get(ticket=ticket)
                    if position_tuple is None or len(position_tuple) == 0:
                        print(f"Position with ticket {ticket} not found.")
                        result_po = mt5.history_deals_get(position=ticket)
                        if result_po is not None:
                            print(f"ticket {ticket} deleted")
                            conn = sqlite3.connect('tickets_bbw.sqlite')
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM order_tickets_bbw_S WHERE order_tickets_bbw_S = ?", (ticket,))
                            conn.commit()
                            conn.close()
                    else:
                        position = position_tuple[0] 
                        volume = position.volume
                        print(f"Volume of position {ticket}: {position}")

                        request = {
                            'action': mt5.TRADE_ACTION_DEAL,
                            'position': ticket,
                            'symbol': symbol,
                            'type': mt5.DEAL_TYPE_BUY,
                            'volume': volume,                        
                            'deviation': 20,
                            'magic': 234002,
                            
                        }
                        result = mt5.order_send(request)
                        if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
                            print(f"Position {ticket} closed successfully")
                            # Delete the ticket from the database
                            conn = sqlite3.connect('tickets_bbw.sqlite')
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM order_tickets_bbw_S WHERE order_tickets_bbw_S = ?", (ticket,))
                            conn.commit()
                            conn.close()
                        else:
                            print(f"Failed to close position {ticket}: {result}")
                            # Delete the ticket from the database
                            conn = sqlite3.connect('tickets_bbw.sqlite')
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM order_tickets_bbw_S WHERE order_tickets_bbw_S = ?", (ticket,))
                            conn.commit()
                            conn.close()
                except Exception as e:
                    print(f"errorrr {ticket} {e} {result}")
                    time.sleep(0.1)
                    # Handle the exception


            global dca_orders_short_bbw
            global dca_orders_bbw
            dca_orders_short_bbw = 0
            dca_orders_bbw = 0

            global current_lot_size_bbw
            global current_lot_size_short_bbw
            current_lot_size_bbw = initial_lot_size_bbw
            current_lot_size_short_bbw = initial_lot_size_short_bbw

            # Connect to the SQLite database (or create it if it doesn't exist)
            conn = sqlite3.connect('memory_live_entries_DB.sqlite')
            # Create a cursor object to execute SQL queries
            cursor = conn.cursor()
            # Update the value in the norm_active table
            cursor.execute("UPDATE bbw_active SET bbw_active = ?", (0,))
            conn.commit()
            conn.close()

        else:
            time.sleep(1)







#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------







# Function to place a pending order
def place_pending_order_oi(order_type, action, price, lot, stop_loss, take_profit):
    symbol = 'BTCUSD'
    request = {
        "action": action,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": stop_loss,
        "tp": take_profit,
        "deviation": 20,
        "magic": 234000,
        "comment": "OI",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    return mt5.order_send(request)


# Main function
def oi_long():
    while True:
        global count_oi_output
        global dca_orders_oi
        global current_lot_size_oi
        take_profit_price = dbTP3 # 10 pips
        stop_loss_price = dbSL3  # 40 pips
        # Calculate new pending order price with a 0.2% decrease
        # Connect to the SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect('memory_live_entries_DB.sqlite')
        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()
        # Update the value in the oi_active table
        cursor.execute("UPDATE oi_active SET oi_active = ?", (1,))
        conn.commit()
        conn.close()   
        live_price =  mt5.symbol_info_tick(symbol).bid
        new_order_price = initial_order_price_oi * (1 - (deviation_percentage_oi * dca_orders_oi))
        truncated_price = round(new_order_price, 2)
        current_lot_size_oi = math.floor(current_lot_size_oi * 100) / 100 # round down 2 decimals

        if dca_orders_oi == 0 and no_first_order == 1:
            dca_orders_oi = dca_orders_oi + 1
        else:
            if dca_orders_oi < max_dca_orders_oi and dd_daily_active == 0 and total_risk_active==0: #and under deviation
                if ema_status == 1 and live_price < truncated_price:
                    if dbSL3 != 0:
                        try:
                            live_price =  mt5.symbol_info_tick(symbol).bid
                            if live_price < truncated_price:
                                truncated_price = live_price
                            order = place_pending_order_oi(mt5.ORDER_TYPE_BUY_LIMIT, mt5.TRADE_ACTION_PENDING, truncated_price, current_lot_size_oi, stop_loss_price, take_profit_price)
                            if order is not None and 'Request executed' in order.comment:
                                print(f'DCA Order placed successfully at price: {truncated_price}') # , order ticket: {order["order"]}
                                # Double the lot size for the next order

                                if no_first_order == 1:
                                    current_lot_size_oi = current_lot_size_oi #* 2
                                else:
                                    current_lot_size_oi = current_lot_size_oi * 2
                                dca_orders_oi = dca_orders_oi + 1

                                # Connect to SQLite database
                                conn = sqlite3.connect('tickets_OI.sqlite')
                                cursor = conn.cursor()
                                # Create table if it doesn't exist
                                cursor.execute('''CREATE TABLE IF NOT EXISTS order_tickets_oi_L (
                                                    order_tickets_oi_L INTEGER
                                                )''')
                                # Function to insert order ticket into the database
                                def insert_order_ticket(order_tickets_oi_L):
                                    cursor.execute("INSERT INTO order_tickets_oi_L (order_tickets_oi_L) VALUES (?)", (order_tickets_oi_L,))
                                    conn.commit()
                                    print("Order ticket inserted successfully.")
                                insert_order_ticket(order.order)
                                conn.close()
                                time.sleep(5)

                            else:
                                print(f'Order placement failed:   lot size: {current_lot_size_short_oi}  ', order)
                                time.sleep(1)
                                dca_orders_oi = dca_orders_oi + 1
                        except Exception as e:
                            print(f'An error occurred while placing the DCA order: {e}')
                            time.sleep(1)
                            dca_orders_oi = dca_orders_oi + 1
                    else:
                        print('stopping OI open trades BREAK')
                        break
                else:
                    if dbSL3 == 0:
                        print('stopping OI open trades BREAK')
                        break

                    time.sleep(0.1)
                    count_oi_output = count_oi_output +1
                    if count_oi_output > 40:
                        count_oi_output = 0
                        try:
                            data = [
                                [f"\033[34mtruncated_price\033[0m", f"\033[34m{truncated_price}\033[0m", f"\033[34mlive_price\033[0m", f"\033[34m{live_price}\033[0m", f"\033[34mema_status\033[0m", f"\033[34m{ema_status}\033[0m", f"\033[34mdca_orders_short_oi\033[0m", f"\033[34m{dca_orders_short_oi}\033[0m"],
                            ]
                            table = tabulate(data, tablefmt="fancy_grid")
                            print(table)
                        except Exception as e:
                            time.sleep(5)
            else:
                print(f"All DCA orders placed. Total orders: {dca_orders_short_oi}")
                print('stopping OI open trades BREAK')
                break  # Exit the loop if the maximum number of orders is reached



def oi_short():
    while True:
        global count_oi_output
        global dca_orders_short_oi
        global current_lot_size_short_oi
        take_profit_price_short = dbTP3  # 10 pips
        stop_loss_price_short = dbSL3  # 40 pips
        # Connect to the SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect('memory_live_entries_DB.sqlite')
        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()
        # Update the value in the oi_active table
        cursor.execute("UPDATE oi_active SET oi_active = ?", (1,))
        conn.commit()
        conn.close()

        live_price =  mt5.symbol_info_tick(symbol).ask
        new_order_price = initial_order_price_short_oi * (1 + (deviation_percentage_short_oi * dca_orders_short_oi))
        truncated_price = round(new_order_price, 2)
        current_lot_size_short_oi = math.floor(current_lot_size_short_oi * 100) / 100 # round down 2 decimals

        if dca_orders_short_oi == 0 and no_first_order == 1:
            dca_orders_short_oi = dca_orders_short_oi + 1
        else:
            if dca_orders_short_oi < max_dca_orders_short_oi and dd_daily_active == 0 and total_risk_active==0: #and under deviation
                if ema_status == -1 and live_price > truncated_price:
                    if dbSL3 != 0:
                        try:
                            # Place pending order
                            live_price =  mt5.symbol_info_tick(symbol).ask
                            if live_price > truncated_price:
                                truncated_price = live_price
                            order = place_pending_order_oi(mt5.ORDER_TYPE_SELL_LIMIT, mt5.TRADE_ACTION_PENDING, truncated_price, current_lot_size_short_oi, stop_loss_price_short, take_profit_price_short)
                            if order is not None and 'Request executed' in order.comment:
                                print(f'DCA Order placed successfully at price: {truncated_price}, lot size: {current_lot_size_short_oi}') # , order ticket: {order["order"]}
                                dca_orders_short_oi = dca_orders_short_oi + 1
                                # Double the lot size for the next order

                                if no_first_order == 1:
                                    current_lot_size_short_oi = current_lot_size_short_oi #* 2
                                else:
                                    current_lot_size_short_oi = current_lot_size_short_oi * 2

                                # Connect to SQLite database
                                conn = sqlite3.connect('tickets_OI.sqlite')
                                cursor = conn.cursor()
                                # Create table if it doesn't exist
                                cursor.execute('''CREATE TABLE IF NOT EXISTS order_tickets_oi_S (
                                                    order_tickets_oi_S INTEGER
                                                )''')
                                # Function to insert order ticket into the database
                                def insert_order_ticket(order_tickets_oi_S):
                                    cursor.execute("INSERT INTO order_tickets_oi_S (order_tickets_oi_S) VALUES (?)", (order_tickets_oi_S,))
                                    conn.commit()
                                    print("Order ticket inserted successfully.")
                                insert_order_ticket(order.order)
                                conn.close()
                                time.sleep(5)

                            else:
                                print(f'Order placement failed:   lot size: {current_lot_size_short_oi}  ', order)
                                time.sleep(1)
                                dca_orders_short_oi = dca_orders_short_oi + 1
                        except Exception as e:
                            print(f'An error occurred while placing the DCA order: {e}')
                            time.sleep(1)
                            dca_orders_short_oi = dca_orders_short_oi + 1
                    else:
                        print('stopping OI open trades BREAK')
                        break
                else:
                    if dbSL3 == 0:
                        print('stopping OI open trades BREAK')
                        break
                    time.sleep(0.1)
                    count_oi_output = count_oi_output +1
                    if count_oi_output > 40:
                        count_oi_output = 0
                        try:
                            data = [
                                [f"\033[34mtruncated_price\033[0m", f"\033[34m{truncated_price}\033[0m", f"\033[34mlive_price\033[0m", f"\033[34m{live_price}\033[0m", f"\033[34mema_status\033[0m", f"\033[34m{ema_status}\033[0m", f"\033[34mdca_orders_short_oi\033[0m", f"\033[34m{dca_orders_short_oi}\033[0m"],
                            ]
                            table = tabulate(data, tablefmt="fancy_grid")
                            print(table)
                        except Exception as e:
                            time.sleep(5)
            else:
                print(f"All DCA orders placed. Total orders: {dca_orders_short_oi}")
                print('stopping OI open trades BREAK')
                #break  # Exit the loop if the maximum number of orders is reached
                break






def oi_orders():
    while True:
        time.sleep(1)
        if time_active == 0 and live_price < (dbTP3 * (1-time_open_threshhold_oi)) and orders_can_be_placed == 1 and dd_daily_active == 0 and total_risk_active==0:
            if dbTP3 != 0 and side3 == 1 and ema_status == 1: # < max_dca_orders_oi
                if oi_active == 0 and dca_orders_oi < max_dca_orders_oi:

                    # Connect to the SQLite database (or create it if it doesn't exist)
                    conn = sqlite3.connect('memory_live_entries_DB.sqlite')
                    # Create a cursor object to execute SQL queries
                    cursor = conn.cursor()
                    # Update the value in the oi_active table
                    cursor.execute("UPDATE oi_active SET oi_active = ?", (1,))
                    conn.commit()
                    conn.close()

                    global initial_order_price_oi
                    if initial_order_price_oi == 0:
                        initial_order_price_oi = mt5.symbol_info_tick(symbol).bid

                    global current_lot_size_oi
                    initial_lot_size_oi = order_size_oi / live_price 
                    current_lot_size_oi = initial_lot_size_oi
                    #current_lot_size_oi = round(current_lot_size_oi, 2)
                    current_lot_size_oi = math.floor(current_lot_size_oi * 100) / 100 # round down 2 decimals
                    # Run oi_long() function in a separate thread
                    long_thread = threading.Thread(target=oi_long)
                    long_thread.start()
                    # Wait for oi_long() to finish
                    long_thread.join()

        if time_active == 0 and live_price > (dbTP3 * (1+time_open_threshhold_oi)) and orders_can_be_placed == 1 and dd_daily_active == 0 and total_risk_active==0:
            if dbTP3 != 0 and side3 == -1 and ema_status == -1: # < max_dca_orders_short_oi
                if oi_active == 0 and dca_orders_short_oi < max_dca_orders_short_oi:

                    # Connect to the SQLite database (or create it if it doesn't exist)
                    conn = sqlite3.connect('memory_live_entries_DB.sqlite')
                    # Create a cursor object to execute SQL queries
                    cursor = conn.cursor()
                    # Update the value in the oi_active table
                    cursor.execute("UPDATE oi_active SET oi_active = ?", (1,))
                    conn.commit()
                    conn.close()

                    global initial_order_price_short_oi
                    if initial_order_price_short_oi == 0:
                        initial_order_price_short_oi = mt5.symbol_info_tick(symbol).ask

                    global current_lot_size_short_oi
                    initial_lot_size_short_oi = order_size_oi / live_price 
                    current_lot_size_short_oi = initial_lot_size_short_oi
                    #current_lot_size_short_oi = round(current_lot_size_short_oi, 2)
                    current_lot_size_short_oi = math.floor(current_lot_size_short_oi * 100) / 100 # round down 2 decimals
                    # Run oi_short() function in a separate thread
                    short_thread = threading.Thread(target=oi_short)
                    short_thread.start()
                    # Wait for oi_short() to finish
                    short_thread.join()






def oi_update():
    while True:
        time.sleep(5)

        # Connect to SQLite database
        conn = sqlite3.connect('tickets_OI.sqlite')
        cursor = conn.cursor()

        # Function to fetch all order ticket values from the database
        def fetch_order_tickets():
            cursor.execute("SELECT * FROM order_tickets_oi_L")
            rows = cursor.fetchall()
            return rows

        # Fetch all order ticket values
        order_tickets = fetch_order_tickets()
        conn.close()

        # Loop through each ticket in the order_tickets list
        for ticket_info in order_tickets:
            tickets = ticket_info[0]  # Extracting the ticket number

            try:
                res = mt5.positions_get(ticket=tickets)
                if res is not None:
                    for position in res:
                        # Access the tp attribute for each position object
                        tp_value = position.tp
                        ticket = position.identifier
                        #print(f"open ticket {tickets} {tp_value} ")
                        if tp_value != dbTP3 and side3 == 1:
                            try:
                                # Update SL and TP for filled orders
                                request = {
                                    'action': mt5.TRADE_ACTION_SLTP,
                                    'position': ticket,
                                    'sl': dbSL3,
                                    'tp': dbTP3
                                }
                                ress = mt5.order_send(request)
                                if ress is not None and 'Request executed' in ress.comment:
                                    print(f"SL and TP updated successfully for order {ticket}")
                                else:
                                    print(f"cant update {ticket} {ress}")
                            except Exception as e:
                                print(f"error exception! {ticket} {e}")
                                time.sleep(5)
            except Exception as e:
                print(f"error exception! {ticket} {e}")
                time.sleep(5)

        # Connect to SQLite database
        conn = sqlite3.connect('tickets_OI.sqlite')
        cursor = conn.cursor()

                # Function to fetch all order ticket values from the database
        def fetch_order_tickets():
            cursor.execute("SELECT * FROM order_tickets_oi_S")
            rows = cursor.fetchall()
            return rows

        # Fetch all order ticket values
        order_tickets = fetch_order_tickets()
        conn.close()

        # Loop through each ticket in the order_tickets list
        for ticket_info in order_tickets:
            tickets = ticket_info[0]  # Extracting the ticket number

            try:
                res = mt5.positions_get(ticket=tickets)
                if res is not None:
                    for position in res:
                        # Access the tp attribute for each position object
                        tp_value = position.tp
                        ticket = position.identifier
                        #print(f"open ticket {tickets} {tp_value} ")
                        if tp_value != dbTP3 and side3 == -1:
                            try:
                                # Update SL and TP for filled orders
                                request = {
                                    'action': mt5.TRADE_ACTION_SLTP,
                                    'position': ticket,
                                    'sl': dbSL3,
                                    'tp': dbTP3
                                }
                                ress = mt5.order_send(request)
                                if ress is not None and 'Request executed' in ress.comment:
                                    print(f"SL and TP updated successfully for order {ticket}")
                                else:
                                    print(f"cant update {ticket} {ress}")
                            except Exception as e:
                                print(f"error exception! {ticket} {e}")
                                time.sleep(5)
            except Exception as e:
                print(f"error exception! {ticket} {e}")
                time.sleep(5)










def close_all_oi():
    time.sleep(1)
    while True:
        if time_active == 1 and side3 == 1 and live_price > (dbTP3 * (1-time_close_threshhold)):
            close_all_true = 1
            print('closing trade before SWAP FEE')
        else:
            close_all_true = 0
        if time_active == 1 and side3 == -1 and live_price < (dbTP3 * (1+time_close_threshhold)):
            close_all_true = 1
            print('closing trade before SWAP FEE')
        else:
            close_all_true = 0
        if dbTP3 == 0 and oi_active != 0 or close_all_true == 1 or oi_needs_reset == 1:
            time.sleep(0.1)
            # Connect to SQLite database
            conn = sqlite3.connect('tickets_OI.sqlite')
            cursor = conn.cursor()

            # Function to fetch all order ticket values from the database
            def fetch_order_tickets():
                cursor.execute("SELECT * FROM order_tickets_oi_L")
                rows = cursor.fetchall()
                return rows

            # Fetch all order ticket values
            order_tickets = fetch_order_tickets()
            conn.close()
            # Loop through each ticket in the order_tickets list
            for ticket_info in order_tickets:
                ticket = ticket_info[0]  # Extracting the ticket number
                try:
                    request = {
                            'action': mt5.TRADE_ACTION_REMOVE,  # Use TRADE_ACTION_REMOVE to close the order
                            'order': ticket,  # Specify the ticket number of the order to close
                        }

                    # Send the order removal request
                    result = mt5.order_send(request)
                    
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"yay {ticket}")
                        # Delete the ticket from the database
                        conn = sqlite3.connect('tickets_OI.sqlite')
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM order_tickets_oi_L WHERE order_tickets_oi_L = ?", (ticket,))
                        conn.commit()
                        conn.close()
                    else:
                        print(f"ORDER with ticket {ticket} not found.")
                        # print(f"cshit {ticket} {ticket} ")
                        # if result is not None and 'Invalid request' in result.comment:
                        #     conn = sqlite3.connect('tickets_OI.sqlite')
                        #     cursor = conn.cursor()
                        #     cursor.execute("DELETE FROM order_tickets_oi_L WHERE order_tickets_oi_L = ?", (ticket,))
                        #     conn.commit()
                        #     conn.close()
                except Exception as e:
                    print(f"errorrr {ticket} {e}")
                    time.sleep(0.1)
                    #print(f"Error: {str(e)}")


            # Loop through each order ticket
            for ticket_info in order_tickets:
                ticket = ticket_info[0]  # Extracting the ticket number
                try:
                    position_tuple = mt5.positions_get(ticket=ticket)
                    if position_tuple is None or len(position_tuple) == 0:
                        print(f"Position with ticket {ticket} not found.")
                        result_po = mt5.history_deals_get(position=ticket)
                        if result_po is not None:
                            print(f"ticket {ticket} deleted")
                            conn = sqlite3.connect('tickets_OI.sqlite')
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM order_tickets_oi_L WHERE order_tickets_oi_L = ?", (ticket,))
                            conn.commit()
                            conn.close()
                    else:
                        position = position_tuple[0] 
                        volume = position.volume
                        print(f"Volume of position {ticket}: {position}")

                        request = {
                            'action': mt5.TRADE_ACTION_DEAL,
                            'position': ticket,
                            'symbol': symbol,
                            'type': mt5.DEAL_TYPE_SELL,
                            'volume': volume,                        
                            'deviation': 20,
                            'magic': 234001,
                            
                        }
                        result = mt5.order_send(request)
                        if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
                            print(f"Position {ticket} closed successfully")
                            # Delete the ticket from the database
                            conn = sqlite3.connect('tickets_OI.sqlite')
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM order_tickets_oi_L WHERE order_tickets_oi_L = ?", (ticket,))
                            conn.commit()
                            conn.close()
                        else:
                            print(f"Failed to close position {ticket}: {result}")
                            # conn = sqlite3.connect('tickets_OI.sqlite')
                            # cursor = conn.cursor()
                            # cursor.execute("DELETE FROM order_tickets_oi_L WHERE order_tickets_oi_L = ?", (ticket,))
                            # conn.commit()
                            # conn.close()
                except Exception as e:
                    print(f"errorrr {ticket} {e}")
                    time.sleep(0.1)
                    # Handle the exception
            

            # Connect to SQLite database
            conn = sqlite3.connect('tickets_OI.sqlite')
            cursor = conn.cursor()

            # Function to fetch all order ticket values from the database
            def fetch_order_tickets():
                cursor.execute("SELECT * FROM order_tickets_oi_S")
                rows = cursor.fetchall()
                return rows

            # Fetch all order ticket values
            order_tickets = fetch_order_tickets()
            conn.close()
            # Loop through each ticket in the order_tickets list
            for ticket_info in order_tickets:
                ticket = ticket_info[0]  # Extracting the ticket number
                try:
                    request = {
                            'action': mt5.TRADE_ACTION_REMOVE,  # Use TRADE_ACTION_REMOVE to close the order
                            'order': ticket,  # Specify the ticket number of the order to close
                        }

                    # Send the order removal request
                    result = mt5.order_send(request)
                    
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"yay {ticket}")
                        # Delete the ticket from the database
                        conn = sqlite3.connect('tickets_OI.sqlite')
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM order_tickets_oi_S WHERE order_tickets_oi_S = ?", (ticket,))
                        conn.commit()
                        conn.close()
                    else:
                        print(f"ORDER with ticket {ticket} not found.")
                        # print(f"cshit {ticket} ")
                        # if result is not None and 'Invalid request' in result.comment:
                        #     conn = sqlite3.connect('tickets_OI.sqlite')
                        #     cursor = conn.cursor()
                        #     cursor.execute("DELETE FROM order_tickets_oi_S WHERE order_tickets_oi_S = ?", (ticket,))
                        #     conn.commit()
                        #     conn.close()
                except Exception as e:
                    print(f"errorrr {ticket} {e}")
                    time.sleep(0.1)
                    #print(f"Error: {str(e)}")


            # Loop through each order ticket
            for ticket_info in order_tickets:
                ticket = ticket_info[0]  # Extracting the ticket number
                try:
                    position_tuple = mt5.positions_get(ticket=ticket)
                    if position_tuple is None or len(position_tuple) == 0:
                        print(f"Position with ticket {ticket} not found.")
                        result_po = mt5.history_deals_get(position=ticket)
                        if result_po is not None:
                            print(f"ticket {ticket} deleted")
                            conn = sqlite3.connect('tickets_OI.sqlite')
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM order_tickets_oi_S WHERE order_tickets_oi_S = ?", (ticket,))
                            conn.commit()
                            conn.close()
                    else:
                        position = position_tuple[0] 
                        volume = position.volume
                        print(f"Volume of position {ticket}: {position}")

                        request = {
                            'action': mt5.TRADE_ACTION_DEAL,
                            'position': ticket,
                            'symbol': symbol,
                            'type': mt5.DEAL_TYPE_BUY,
                            'volume': volume,                        
                            'deviation': 20,
                            'magic': 234002,
                            
                        }
                        result = mt5.order_send(request)
                        if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
                            print(f"Position {ticket} closed successfully")
                            # Delete the ticket from the database
                            conn = sqlite3.connect('tickets_OI.sqlite')
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM order_tickets_oi_S WHERE order_tickets_oi_S = ?", (ticket,))
                            conn.commit()
                            conn.close()
                        else:
                            print(f"Failed to close position {ticket}: {result}")
                            conn = sqlite3.connect('tickets_OI.sqlite')
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM order_tickets_oi_S WHERE order_tickets_oi_S = ?", (ticket,))
                            conn.commit()
                            conn.close()
                except Exception as e:
                    print(f"errorrr {ticket} {e}")
                    time.sleep(0.1)
                    # Handle the exception

            global dca_orders_short_oi
            global dca_orders_oi
            dca_orders_short_oi = 0
            dca_orders_oi = 0

            global current_lot_size_oi
            global current_lot_size_short_oi
            current_lot_size_oi = initial_lot_size_oi
            current_lot_size_short_oi = initial_lot_size_short_oi

            global initial_order_price_oi
            initial_order_price_oi = 0
            global initial_order_price_short_oi
            initial_order_price_short_oi = 0

            # Connect to the SQLite database (or create it if it doesn't exist)
            conn = sqlite3.connect('memory_live_entries_DB.sqlite')
            # Create a cursor object to execute SQL queries
            cursor = conn.cursor()
            # Update the value in the norm_active table
            cursor.execute("UPDATE oi_active SET oi_active = ?", (0,))
            conn.commit()
            conn.close()

        else:
            time.sleep(1)






#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




def active_norm_tickets():
    while True:
        time.sleep(0.2)
        global norm_needs_reset
        if norm_active != 0 and side1 == 1 and live_price > dbTP1:
            norm_needs_reset = 1
            print('norm_needs_reset TP hit')
        else:
            if norm_active != 0 and side1 == -1 and live_price < dbTP1:
                norm_needs_reset = 1
                print('norm_needs_reset TP hit')
            else:
                norm_needs_reset = 0

        

def active_bbw_tickets():
    while True:
        time.sleep(0.2)
        global bbw_needs_reset
        if bbw_active != 0 and side2 == 1 and live_price > dbTP2:
            bbw_needs_reset = 1
            print('bbw_needs_reset TP hit')
        else:
            if bbw_active != 0 and side2 == -1 and live_price < dbTP2:
                bbw_needs_reset = 1
                print('bbw_needs_reset TP hit')
            else:
                bbw_needs_reset = 0



def active_oi_tickets():
    while True:
        time.sleep(0.2)
        global oi_needs_reset
        if oi_active != 0 and side3 == 1 and live_price > dbTP3:
            oi_needs_reset = 1
            print('oi_needs_reset TP hit')
        else:
            if oi_active != 0 and side3 == -1 and live_price < dbTP3:
                oi_needs_reset = 1
                print('oi_needs_reset TP hit')
            else:
                oi_needs_reset = 0




#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def start_chart():
    time.sleep(0.2)
    font_size = 15
    padding_size = 3

    root = tk.Tk()
    root.title("OUTPUT")

    style = ttk.Style(root)
    root.tk.call("source", "forest-dark.tcl")
    style.theme_use("forest-dark")

    frame = ttk.Frame(root)
    frame.grid(row=0,column=0)

    frame_2 = ttk.Frame(root)
    frame_2.grid(row=0,column=1)

    def on_closing():
        conn.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    norm_orders_frame = ttk.Labelframe(frame, text="normal order details")
    norm_orders_frame.grid(row=0,column=0)

    bbw_orders_frame = ttk.Labelframe(frame, text="BBW order details")
    bbw_orders_frame.grid(row=1,column=0)

    oi_orders_frame = ttk.Labelframe(frame, text="OI order details")
    oi_orders_frame.grid(row=2,column=0)

    details_frame = ttk.Labelframe(frame, text="details")
    details_frame.grid(row=3,column=0)

    spread_frame = ttk.Labelframe(frame, text="spread live")
    spread_frame.grid(row=4,column=0)

    # euity_frame = ttk.Frame(frame_2)
    # euity_frame.grid(row=0,column=0)

    #     # Create Matplotlib Figure and Axis
    # fig, ax = plt.subplots()
    # canvas = FigureCanvasTkAgg(fig, master=euity_frame)
    # canvas.get_tk_widget().grid(row=0,column=0)



    text_label_TP = ttk.Label(norm_orders_frame, text="TP")
    text_label_TP.grid(row=0,column=0)
    text_label_SL = ttk.Label(norm_orders_frame, text="SL")
    text_label_SL.grid(row=1,column=0)
    text_label_side = ttk.Label(norm_orders_frame, text="side")
    text_label_side.grid(row=2,column=0)
    text_label_active = ttk.Label(norm_orders_frame, text="Norm active")
    text_label_active.grid(row=3,column=0)

    text_label_TP_bbw = ttk.Label(bbw_orders_frame, text="TP")
    text_label_TP_bbw.grid(row=0,column=0)
    text_label_SL_bbw = ttk.Label(bbw_orders_frame, text="SL")
    text_label_SL_bbw.grid(row=1,column=0)
    text_label_side_bbw = ttk.Label(bbw_orders_frame, text="side")
    text_label_side_bbw.grid(row=2,column=0)
    text_label_active_bbw = ttk.Label(bbw_orders_frame, text="BBW active")
    text_label_active_bbw.grid(row=3,column=0)

    text_label_TP_oi = ttk.Label(oi_orders_frame, text="TP")
    text_label_TP_oi.grid(row=0,column=0)
    text_label_SL_oi = ttk.Label(oi_orders_frame, text="SL")
    text_label_SL_oi.grid(row=1,column=0)
    text_label_side_oi = ttk.Label(oi_orders_frame, text="side")
    text_label_side_oi.grid(row=2,column=0)
    text_label_active_oi = ttk.Label(oi_orders_frame, text="OI active")
    text_label_active_oi.grid(row=3,column=0)
    text_dca_orders_short_oi = ttk.Label(oi_orders_frame, text="OI position amount")
    text_dca_orders_short_oi.grid(row=4,column=0)

    text_ema_status = ttk.Label(details_frame, text="EMA status")
    text_ema_status.grid(row=0,column=0)
    text_time_active = ttk.Label(details_frame, text="time active")
    text_time_active.grid(row=1,column=0)
    text_orders_can_be_placed = ttk.Label(details_frame, text="can orders be placed")
    text_orders_can_be_placed.grid(row=2,column=0)
    text_dd_daily_active = ttk.Label(details_frame, text="Daily Drawdown active")
    text_dd_daily_active.grid(row=3,column=0)
    text_dd_percentage = ttk.Label(details_frame, text="Daily Drawdown %")
    text_dd_percentage.grid(row=4,column=0)
    text_total_risk_active = ttk.Label(details_frame, text="risk active")
    text_total_risk_active.grid(row=6,column=0)
    text_deals_in_history = ttk.Label(details_frame, text="deals in history")
    text_deals_in_history.grid(row=5,column=0)
    text_risk_P = ttk.Label(details_frame, text="risk %")
    text_risk_P.grid(row=7,column=0)

    text_spread = ttk.Label(spread_frame, text="%")
    text_spread.grid(row=0,column=0)
    


    # Function to update label_text whenever dbTP1 changes
    def update_label_text():
        label_dbTP1.set(dbTP1)
        label_dbTP2.set(dbTP2)
        label_dbTP3.set(dbTP3)
        label_dbSL1.set(dbSL1)
        label_dbSL2.set(dbSL2)
        label_dbSL3.set(dbSL3)
        label_side1.set(side1)
        label_side2.set(side2)
        label_side3.set(side3)
        label_norm_active.set(norm_active)
        label_bbw_active.set(bbw_active)
        label_oi_active.set(oi_active)
        label_ema_status.set(ema_status)
        label_time_active.set(time_active)
        label_orders_can_be_placed.set(orders_can_be_placed)
        label_dd_daily_active.set(dd_daily_active)
        label_dd_percentage.set(max_drawdown)
        label_total_risk_active.set(total_risk_active)
        label_deals_in_history.set(deals_in_history)
        label_dca_orders_short_oi.set(dca_orders_short_oi)
        label_risk_P.set(risk_total_global)
        label_spread_now.set(spread_now)



    label_dbTP1 = tk.StringVar(value=dbTP1)
    label_dbTP2 = tk.StringVar(value=dbTP2)
    label_dbTP3 = tk.StringVar(value=dbTP3)

    label_dbSL1 = tk.StringVar(value=dbSL1)
    label_dbSL2 = tk.StringVar(value=dbSL2)
    label_dbSL3 = tk.StringVar(value=dbSL3)

    label_side1 = tk.StringVar(value=side1)
    label_side2 = tk.StringVar(value=side2)
    label_side3 = tk.StringVar(value=side3)

    label_norm_active = tk.StringVar(value=norm_active)
    label_bbw_active = tk.StringVar(value=bbw_active)
    label_oi_active = tk.StringVar(value=oi_active)

    label_ema_status = tk.StringVar(value=ema_status)
    label_time_active = tk.StringVar(value=time_active)
    label_orders_can_be_placed = tk.StringVar(value=orders_can_be_placed)
    label_dd_daily_active = tk.StringVar(value=dd_daily_active)
    label_dd_percentage = tk.StringVar(value=dd_percentage)

    label_total_risk_active = tk.StringVar(value=total_risk_active)
    label_deals_in_history = tk.StringVar(value=deals_in_history)
    label_dca_orders_short_oi = tk.StringVar(value=dca_orders_short_oi)
    label_risk_P = tk.StringVar(value=risk_total_global)
    label_spread_now = tk.StringVar(value=spread_now)  # Initialize label_spread_now

    # Create labels using the StringVar variables
    live_label_dbTP1 = ttk.Label(norm_orders_frame, textvariable=label_dbTP1, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_dbTP2 = ttk.Label(bbw_orders_frame, textvariable=label_dbTP2, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_dbTP3 = ttk.Label(oi_orders_frame, textvariable=label_dbTP3, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))

    live_label_dbSL1 = ttk.Label(norm_orders_frame, textvariable=label_dbSL1, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_dbSL2 = ttk.Label(bbw_orders_frame, textvariable=label_dbSL2, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_dbSL3 = ttk.Label(oi_orders_frame, textvariable=label_dbSL3, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))

    live_label_side1 = ttk.Label(norm_orders_frame, textvariable=label_side1, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_side2 = ttk.Label(bbw_orders_frame, textvariable=label_side2, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_side3 = ttk.Label(oi_orders_frame, textvariable=label_side3, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))

    live_label_norm_active = ttk.Label(norm_orders_frame, textvariable=label_norm_active, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_bbw_active = ttk.Label(bbw_orders_frame, textvariable=label_bbw_active, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_oi_active = ttk.Label(oi_orders_frame, textvariable=label_oi_active, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))

    live_label_dca_orders_short_oi = ttk.Label(oi_orders_frame, textvariable=label_dca_orders_short_oi, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))

    live_label_ema_status = ttk.Label(details_frame, textvariable=label_ema_status, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_time_active = ttk.Label(details_frame, textvariable=label_time_active, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_orders_can_be_placed = ttk.Label(details_frame, textvariable=label_orders_can_be_placed, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_dd_daily_active = ttk.Label(details_frame, textvariable=label_dd_daily_active, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_dd_percentage = ttk.Label(details_frame, textvariable=label_dd_percentage, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))

    live_label_total_risk_active = ttk.Label(details_frame, textvariable=label_total_risk_active, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_deals_in_history = ttk.Label(details_frame, textvariable=label_deals_in_history, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))
    live_label_risk_P = ttk.Label(details_frame, textvariable=label_risk_P, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size))

    live_spread_now = ttk.Label(spread_frame, textvariable=label_spread_now, borderwidth=2, relief="groove", padding=padding_size,font=("Times",font_size)) 

    # Pack the labels using the pack() method
    live_label_dbTP1.grid(row=0,column=1)
    live_label_dbTP2.grid(row=0,column=1)
    live_label_dbTP3.grid(row=0,column=1)

    live_label_dbSL1.grid(row=1,column=1)
    live_label_dbSL2.grid(row=1,column=1)
    live_label_dbSL3.grid(row=1,column=1)

    live_label_side1.grid(row=2,column=1)
    live_label_side2.grid(row=2,column=1)
    live_label_side3.grid(row=2,column=1)

    live_label_norm_active.grid(row=3,column=1)
    live_label_bbw_active.grid(row=3,column=1)
    live_label_oi_active.grid(row=3,column=1)

    live_label_dca_orders_short_oi.grid(row=4,column=1)

    live_label_ema_status.grid(row=0,column=1)
    live_label_time_active.grid(row=1,column=1)
    live_label_orders_can_be_placed.grid(row=2,column=1)
    live_label_dd_daily_active.grid(row=3,column=1)
    live_label_dd_percentage.grid(row=4,column=1)

    live_label_total_risk_active.grid(row=6,column=1)
    live_label_deals_in_history.grid(row=5,column=1)
    live_label_risk_P.grid(row=7,column=1)
    live_spread_now.grid(row=0,column=1)

    def simulate_db_change():
        update_label_text()
        root.after(500, simulate_db_change)  # Update every 1 second

    simulate_db_change()

    root.mainloop()






if __name__ == '__main__':
    #thread_a = threading.Thread(target=run_worker_program)
    thread_b = threading.Thread(target=run_wsgi_program)
    thread_c = threading.Thread(target=run_chart_program)

    thread0 = threading.Thread(target=start_chart)

    thread1 = threading.Thread(target=update_memory_DB)
    thread2 = threading.Thread(target=norm_orders)
    thread3 = threading.Thread(target=norm_update)
    thread4 = threading.Thread(target=close_all_norm)

    thread6 = threading.Thread(target=orders_bbw)
    thread7 = threading.Thread(target=update_bbw)
    thread8 = threading.Thread(target=close_all_bbw)

    thread9 = threading.Thread(target=oi_orders)
    thread10 = threading.Thread(target=oi_update)
    thread11 = threading.Thread(target=close_all_oi)

    thread12 = threading.Thread(target=lot_sizes)
    thread13 = threading.Thread(target=update_memory_DB_2)
    thread14 = threading.Thread(target=risk_calculation)
    thread15 = threading.Thread(target=account_inactive_trade)
    thread16 = threading.Thread(target=insert_equity_data)

    thread17 = threading.Thread(target=active_norm_tickets)
    thread18 = threading.Thread(target=active_bbw_tickets)
    thread19 = threading.Thread(target=active_oi_tickets)

    thread_b.start()
    #thread_a.start()
    thread_c.start()

    thread0.start()
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()

    thread6.start()
    thread7.start()
    thread8.start()

    thread9.start()
    thread10.start()
    thread11.start()

    thread12.start()
    thread13.start()
    thread14.start()
    thread15.start()
    thread16.start()

    thread17.start()
    thread18.start()
    thread19.start()

    # Wait for all threads to finish

    thread_b.join()
    #thread_a.join()
    thread_c.join()

    thread0.join()
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()

    thread6.join()
    thread7.join()
    thread8.join()

    thread9.join()
    thread10.join()
    thread11.join()

    thread12.join()
    thread13.join()
    thread14.join()
    thread15.join()
    thread16.join()

    thread17.join()
    thread18.join()
    thread19.join()









