import time
import hmac
import hashlib
import requests
import logging 
import os 
from dotenv import load_dotenv

load_dotenv()

BASE_URL = 'https://fapi.binance.com'
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")




def _sign(params):
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    return hmac.new(api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def _post(endpoint, params):
    params['timestamp'] = int(time.time() * 1000)
    params['signature'] = _sign(params)
    headers = {"X-MBX-APIKEY": api_key}
    response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, params=params)
    try:
        response.raise_for_status()
    except Exception as e:
        logging.error("HTTP Error: ", e)
        logging.error("Response body:", response.text)
    return response.json()

def cancel_stop_market_orders(symbol, orderid):
    logging.info(f"Attempting to cancel orderid: {orderid}")
    url = f"{BASE_URL}/fapi/v1/order"

    headers = {
        'X-MBX-APIKEY': api_key
    }

    timestamp = int(time.time() * 1000)
    params = {
        'symbol': symbol.upper(),
        'orderId': orderid,
        'timestamp': timestamp
    }
    params['signature'] = _sign(params)

    try: 
        response = requests.delete(url, headers=headers, params=params)
        if response.status_code == 200: 
            logging.info(f"✅ Stop loss order {orderid} for {symbol} canceled.")
            return response.json()
        else:
            logging.warning(f"❌ Error canceling Stop loss order: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        logging.error(f"⚠️ Request exception: {e}")


def set_stop_loss(symbol, side, stop_price, quantity):
    params = {
        'symbol': symbol,
        'side': side,
        'type': 'STOP_MARKET',
        'stopPrice': format(stop_price, '.2f'),
        'quantity': quantity,
        'timestamp': int(time.time() * 1000)
    }
    try:
        res = _post('/fapi/v1/order', params)
        logging.info(f"Successfully executed STOPLOSS ORDER with ID: {res['orderId']}")
        return res
    except Exception as e:
        logging.error(f"An error occurred in BinanceFuturesTrader.set_stop_loss | Error: {e}")
        raise e