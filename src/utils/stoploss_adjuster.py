import time
import hmac
import hashlib
import requests
import logging 
import os 
from dotenv import load_dotenv
from src.utils.supabase_client_post import log_into_supabase

load_dotenv()

BASE_URL = 'https://fapi.binance.com'
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
supabase_url = os.getenv("SUPABASE_URL")
supbase_api_key = os.getenv("SUPABASE_API_KEY")
supabase_jwt = os.getenv("SUPABASE_JWT")

def _sign(self, params):
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    return hmac.new(api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def _post(self, endpoint, params):
    params['timestamp'] = int(time.time() * 1000)
    params['signature'] = self._sign(params)
    headers = {"X-MBX-APIKEY": self.api_key}
    response = requests.post(f"{self.BASE_URL}{endpoint}", headers=headers, params=params)
    try:
        response.raise_for_status()
    except Exception as e:
        logging.error("HTTP Error: ", e)
        logging.error("Response body:", response.text)
    return response.json()

def cancel_stop_market_orders(symbol, orderid):
    url = f"{BASE_URL}/fapi/v1/order"

    headers = {
        'X-MBX-APIKEY': api_key
    }

    while True: 
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

        time.sleep(5)

def set_stop_loss(symbol, side, stop_price, quantity):
    params = {
        'symbol': symbol,
        'side': side,
        'type': 'STOP_MARKET',
        'stopPrice': stop_price,
        'quantity': quantity,
        'timeInForce': 'GTC'
    }
    try:
        res = _post('/fapi/v1/order', params)
        logging.info(f"Successfully executed STOPLOSS ORDER with ID: {res['orderId']}")
        return res
    except Exception as e:
        logging.error(f"An error occurred in BinanceFuturesTrader.set_stop_loss | Error: {e}")
        raise


def adjust_SL(orderid, symbol, side, stop_price, quantity, group_id):
    cancel_stop_market_orders(symbol, orderid)
    new_stoploss = set_stop_loss(symbol, side, stop_price, quantity)
    stoploss_order_id = new_stoploss['orderId']

    data_side = "LONG" if side == "SELL" else "SHORT"

    # Log new stop loss into Supabase       
    data = {
        "group_id": group_id,
        "order_id": stoploss_order_id,
        "type": "NSL",
        "side": data_side,
        "breakeven_threshold": 0.00,
        "breakeven_price": 0.00
    }

    try:
        log_into_supabase(data, supabase_url=supabase_url, api_key=supbase_api_key, jwt=supabase_jwt)
        logging.info("NEW STOPLOSS Trade logged to Supabase")
    
    except Exception as e:
        logging.error(f"Failed to log NEW STOPLOSS trade to Supabase: {e}")