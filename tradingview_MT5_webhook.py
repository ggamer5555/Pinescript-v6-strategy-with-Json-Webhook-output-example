from flask import Flask, request, jsonify
import asyncio, json, time # , websockets, requests
#from web3 import Web3
#import ccxt 
#from termcolor import colored
import numpy as np
#import decimal
import sqlite3
import os
import hashlib
import config
from waitress import serve
#from dotenv import load_dotenv
from functools import wraps
import logging
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter

#-----------------------------------------------------------------------------------------------------------------------------------

# GREEN = '\033[92m'
# CRED = '\033[91m'
# CEND = '\033[0m'


# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='wsgiflask.log',
    filemode='a'
)

# Get named logger
logger = logging.getLogger(__name__)

# Create handler
handler = TimedRotatingFileHandler(filename='runtimewsgi.log', when='D', interval=1, backupCount=30, encoding='utf-8', delay=False)

# Create formatter and add it to the handler
formatter = Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the named logger
logger.addHandler(handler)

# Set the logging level
logger.setLevel(logging.INFO)



# async def fetch_order():
#     exchange = ccxt.bybit()
#     exchange.load_time_difference()
#     print(exchange.options['timeDifference'])

# # Call the async function
# asyncio.run(fetch_order())

passs = config.PASSPHRASE

# Define the allowed IP addresses
allowed_ips = ['52.89.214.238', '34.212.75.30', '54.218.53.128', '52.32.178.7']

# flask --app bybit_web_sec run
app = Flask(__name__)

@app.route('/')
def index():
    return 'shh'


#-----------------------------------------------------------------------------------------------------------------------------------

# conn = sqlite3.connect('bybit_webhook_DB.sqlite', check_same_thread=False) # ? maybe should be true
# conn.execute('PRAGMA journal_mode = wal')
# conn.execute('PRAGMA locking_mode = NORMAL')  # maybe not needed
# # Set automatic checkpointing to occur after every N database pages
# # Adjust the value of N as per your requirements
# conn.execute('PRAGMA wal_autocheckpoint = 1') # i think low is good  , automatic checkpoint will be triggered after every 1000 database pages have been written to the WAL file

# conn = sqlite3.connect('bybit_webhook_2_DB.sqlite', check_same_thread=False) # ? maybe should be true
# conn.execute('PRAGMA journal_mode = wal')
# conn.execute('PRAGMA locking_mode = NORMAL')  # maybe not needed
# # Set automatic checkpointing to occur after every N database pages
# # Adjust the value of N as per your requirements
# conn.execute('PRAGMA wal_autocheckpoint = 1') # i think low is good  , automatic checkpoint will be triggered after every 1000 database pages have been written to the WAL file



# def create_table():     # only used to create a table then sets them to NONE so then they need to be set to 0
#     conn.execute('''CREATE TABLE IF NOT EXISTS bybit_webhook_DB (
#         Wprice_db TEXT,
#         order_side_db TEXT,
#         take_profit_price_db TEXT,
#         stop_loss_db TEXT,
#         live_stat_db TEXT
#     )''')
#     conn.commit()

# create_table()

# def create_table():     # only used to create a table then sets them to NONE so then they need to be set to 0
#     conn.execute('''CREATE TABLE IF NOT EXISTS bybit_webhook_2_DB (
#         ht_ema_db TEXT,
#         P_C_ema_db TEXT,
#         strategy_db TEXT,
#         close_bbw_db TEXT,
#         close_v_db TEXT
#     )''')
#     conn.commit()

# create_table()

# def check_Wprice():
#     c1.execute("SELECT Wprice_db FROM bybit_webhook_DB ORDER BY Wprice_db DESC LIMIT 1")
#     Wprice_db = c1.fetchone()[0]
#     print('Wprice_db : ',Wprice_db)
#     return Wprice_db

# def check_order_side():
#     c2.execute("SELECT order_side_db FROM bybit_webhook_DB ORDER BY order_side_db DESC LIMIT 1")
#     order_side_db = c2.fetchone()[0]
#     print('order_side_db : ', order_side_db)
#     return order_side_db

# def check_take_profit_price():
#     c3.execute("SELECT take_profit_price_db FROM bybit_webhook_DB ORDER BY take_profit_price_db DESC LIMIT 1")
#     take_profit_price_db = c3.fetchone()[0]
#     print('take_profit_price_db : ', take_profit_price_db)
#     return take_profit_price_db

# def check_stop_loss():
#     c4.execute("SELECT stop_loss_db FROM bybit_webhook_DB ORDER BY stop_loss_db DESC LIMIT 1")
#     stop_loss_db = c4.fetchone()[0]
#     print('stop_loss_db : ', stop_loss_db)
#     return stop_loss_db

#-----------------------------------------------------------------------------------------------------------------------------------
#zero = 0
# def reset_db_values():
#     # this updates the values to 0 
#     conn.execute("UPDATE bybit_webhook_DB SET Wprice_db = ?, order_side_db = ?, take_profit_price_db = ?, stop_loss_db = ?",(zero, zero, zero, zero,))
#     conn.commit()


# def insert_db_values(): 
#     # required if type = NONE    then set to 0 to start
#     conn.execute("INSERT INTO bybit_webhook_DB (Wprice_db, order_side_db, take_profit_price_db, stop_loss_db) VALUES (?, ?, ?, ?, ?)", (zero, zero, zero, zero))
#     conn.commit()

# insert_db_values()

#-----------------------------------------------------------------------------------------------------------------------------------

# insert_db_values()
# check_Wprice()
# check_order_side()
# check_stop_loss()
# check_take_profit_price()


#----------------------------------------------------------------------------------------------------------------------------------


# {
#     "passphrase": "yourpassphrase",
#     "time": "{{timenow}}",
#     "exchange": "{{exchange}}",
#     "ticker": "{{ticker}}",
#     "time2": "{{time}}",
#     "TP": "{{alert_message}}",
#     "ht_ema": "{{plot_0}}",
#     "P_C_ema": "{{plot_1}}",
#     "order_side": "{{plot_2}}",
#     "Wprice": "{{plot_3}}",
#     "SL_price": "{{plot_4}}",
#     "strategy": "{{plot_5}}",
#     "close_bbw": "{{plot_6}}",
#     "close_v": "{{plot_7}}"
# }


# zero = 0

# # conn = sqlite3.connect('bybit_webhook_2_DB.sqlite', check_same_thread=False) # ? maybe should be true
# # conn.execute('PRAGMA journal_mode = wal')
# # conn.execute('PRAGMA locking_mode = NORMAL')  # maybe not needed
# # conn.execute('PRAGMA wal_autocheckpoint = 1') # i think low is good  , automatic checkpoint will be triggered after every 1000 database pages have been written to the WAL file
# conn.execute("INSERT INTO bybit_webhook_2_DB (ht_ema_db, P_C_ema_db, strategy_db, close_bbw_db, close_v_db) VALUES (?, ?, ?, ?, ?)", (zero, zero, zero, zero, zero))
# conn.commit()
# conn.close()




# @app.route('/test', methods=['POST'])
# def webhook():
#     webhook_message = json.loads(request.data)

#     # Input validation
#     required_fields = ['passphrase','Wprice', 'order_side', 'TP', 'SL_price', 'strategy', 'ht_ema', 'P_C_ema', 'close_v', 'close_bbw']
#     for field in required_fields:
#         if field not in webhook_message:
#             return jsonify({
#                 'code': 'error',
#                 'message': f'F'
#             }), 400

#     # Input validation for numeric fields
#     numeric_fields = ['Wprice', 'order_side', 'TP', 'SL_price', 'strategy', 'ht_ema', 'P_C_ema', 'close_v', 'close_bbw']
#     for field in numeric_fields:
#         if not is_numeric(webhook_message[field]):
#             return jsonify({
#                 'code': 'error',
#                 'message': f'FF'
#             }), 400

#     # Compare hashed passphrases
#     input_passphrase = webhook_message.get('passphrase', '')
#     stored_passphrase = passs
#     hashed_input_passphrase = hashlib.sha256(input_passphrase.encode()).hexdigest()

#     if hashed_input_passphrase != stored_passphrase:
#         return jsonify({
#             'code': 'error',
#             'message': 'L'
#         }), 401
    
#     # Update bybit_webhook_DB
#     con = sqlite3.connect('bybit_webhook_DB.sqlite', check_same_thread=False)
#     con.execute('PRAGMA journal_mode = wal')
#     con.execute('PRAGMA locking_mode = NORMAL')
#     con.execute('PRAGMA wal_autocheckpoint = 10')

#     # Use parameterized queries
#     query = "UPDATE bybit_webhook_DB SET Wprice_db=?, order_side_db=?, take_profit_price_db=?, stop_loss_db=?, strategy_db=?"
#     values = (webhook_message['Wprice'], webhook_message['order_side'], webhook_message['TP'],
#               webhook_message['SL_price'], webhook_message['strategy'])
#     con.execute(query, values)
#     con.commit()
#     con.close()

#     # Update bybit_webhook_2_DB
#     conn = sqlite3.connect('bybit_webhook_2_DB.sqlite', check_same_thread=False)
#     conn.execute('PRAGMA journal_mode = wal')
#     conn.execute('PRAGMA locking_mode = NORMAL')
#     conn.execute('PRAGMA wal_autocheckpoint = 10')

#     # Use parameterized queries
#     query = "UPDATE bybit_webhook_2_DB SET ht_ema_db=?, P_C_ema_db=?, close_v_db=?, close_bbw_db=?"
#     values = (webhook_message['ht_ema'], webhook_message['P_C_ema'], webhook_message['close_v'], webhook_message['close_bbw'])
#     conn.execute(query, values)
#     conn.commit()
#     conn.close()

#     return jsonify({
#         'code': 'error',
#         'message': 'K'
#     }), 200


# def is_numeric(value):
#     try:
#         float(value)
#         return True
#     except (ValueError, TypeError):
#         return False


def initialize_memory_db():
    conn = sqlite3.connect('memory_DB.sqlite', check_same_thread=False)
    conn.execute('PRAGMA journal_mode = wal')
    conn.execute('PRAGMA locking_mode = NORMAL')
    conn.execute('PRAGMA wal_autocheckpoint = 1')

    conn.execute('''CREATE TABLE IF NOT EXISTS memory_DB (
                    side1 REAL DEFAULT 0,
                    side2 REAL DEFAULT 0,
                    side3 REAL DEFAULT 0,
                    TP1 REAL DEFAULT 0,
                    TP2 REAL DEFAULT 0,
                    TP3 REAL DEFAULT 0,
                    SL1 REAL DEFAULT 0,
                    SL2 REAL DEFAULT 0,
                    SL3 REAL DEFAULT 0
                    )''')

    zero = 0
    conn.execute("INSERT INTO memory_DB (side1, side2, side3, TP1, TP2, TP3, SL1, SL2, SL3) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 (zero, zero, zero, zero, zero, zero, zero, zero, zero))
    conn.commit()
    conn.close()

# Call the function to initialize memory_DB
#initialize_memory_db()

# def insert_into_memory_db(data, ema_value):
#     conn = sqlite3.connect('memory_DB.sqlite', check_same_thread=False)
#     conn.execute('PRAGMA journal_mode = wal')
#     conn.execute('PRAGMA locking_mode = NORMAL')
#     conn.execute('PRAGMA wal_autocheckpoint = 10')

#     query = "INSERT INTO memory_DB (side1, side2, side3, TP1, TP2, TP3, SL1, SL2, SL3) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
#     values = (
#         data['side1'], data['side2'], data['side3'],
#         data['TP1'], data['TP2'], data['TP3'],
#         data['SL1'], data['SL2'], data['SL3']
#     )
#     conn.execute(query, values)
#     # Insert EMA value into the EMA_status table
#     ema_query = "INSERT INTO EMA_status (EMA) VALUES (?)"
#     ema_values = (ema_value,)
#     conn.execute(ema_query, ema_values)

#     conn.commit()
#     conn.close()

def insert_into_memory_db(data, ema_value):
    conn = sqlite3.connect('memory_DB.sqlite', check_same_thread=False)
    conn.execute('PRAGMA journal_mode = wal')
    conn.execute('PRAGMA locking_mode = NORMAL')
    conn.execute('PRAGMA wal_autocheckpoint = 10')

    # Update the existing row with the new data
    query = """
        UPDATE memory_DB
        SET side1 = ?, side2 = ?, side3 = ?,
            TP1 = ?, TP2 = ?, TP3 = ?,
            SL1 = ?, SL2 = ?, SL3 = ?
        WHERE rowid = 1
    """
    values = (
        data['side1'], data['side2'], data['side3'],
        data['TP1'], data['TP2'], data['TP3'],
        data['SL1'], data['SL2'], data['SL3']
    )
    conn.execute(query, values)

    # Replace the existing EMA value with the new one
    ema_query = """
        UPDATE EMA_status
        SET EMA = ?
        WHERE rowid = 1
    """
    ema_values = (ema_value,)
    conn.execute(ema_query, ema_values)

    conn.commit()
    conn.close()


# ip_address in allowed_ips and 
def only_post_allowed(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip_address = request.remote_addr  # Get the IP address of the requester
        if request.method == 'POST':
            return f(*args, **kwargs)
        else:
            logging.critical('Unauthorized access attempt from IP: %s', ip_address)
            print('ip_address')
            return "Unauthorized", 401  # Return unauthorized status code if conditions are not met
    return decorated_function


@app.route('/test', methods=['POST'])
@only_post_allowed
def webhook():
    webhook_message = json.loads(request.data)
    log_message = {key: value for key, value in webhook_message.items() if key != 'passphrase'}
    logging.info('Received webhook message: %s', log_message)

    # Input validation
    required_fields = ['passphrase', 'side1', 'side2', 'side3', 'TP1', 'TP2', 'TP3', 'SL1', 'SL2', 'SL3', 'EMA']
    for field in required_fields:
        if field not in webhook_message:
            return jsonify({
                'code': 'error',
                'message': f'F'
            }), 400

    # Input validation for numeric fields
    numeric_fields = ['side1', 'side2', 'side3', 'TP1', 'TP2', 'TP3', 'SL1', 'SL2', 'SL3', 'EMA']
    for field in numeric_fields:
        if not is_numeric(webhook_message[field]):
            return jsonify({
                'code': 'error',
                'message': f'FF'
            }), 400

    # Compare hashed passphrases
    input_passphrase = webhook_message.get('passphrase', '')
    stored_passphrase = passs
    hashed_input_passphrase = hashlib.sha256(input_passphrase.encode()).hexdigest()

    if hashed_input_passphrase != stored_passphrase:
        return jsonify({
            'code': 'error',
            'message': 'L'
        }), 401
    
    # Extract EMA value from the webhook message
    ema_value = webhook_message['EMA']

    # Insert data into the memory_DB database
    insert_into_memory_db(webhook_message, ema_value)

    return jsonify({
        'code': 'error',
        'message': 'K'
    }), 200


def is_numeric(value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False




