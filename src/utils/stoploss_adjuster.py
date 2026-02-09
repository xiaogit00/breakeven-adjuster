from src.services import binanceREST
from src.services import db
from src.utils.supabase_client_post import log_into_supabase
import logging
import time
import json

def adjust_SL_order(order_enriched, candle_price):
    logging.info(f"Attempting to adjust SL the following order: {order_enriched}")

    order_id = order_enriched['order_id']
    symbol = order_enriched['symbol']
    side = order_enriched['side']
    next_stoploss_price = round(float(order_enriched['order_group_data']['next_stoploss_price']), 4)
    qty = order_enriched['qty']
    group_id = order_enriched['order_group_data']['group_id']
    binanceREST.cancel_algo_order(symbol, order_id)
    time.sleep(2)
    new_SL_order_id = None
    try:
        new_stoploss_order = binanceREST.execute_stop_loss_algo_order(symbol, side, next_stoploss_price, qty)
        new_SL_order_id = new_stoploss_order.get('algoId')
    except:
        logging.error("Attempting to retry set stop loss...")
        time.sleep(1)
        new_stoploss_order = binanceREST.execute_stop_loss_algo_order(symbol, side, next_stoploss_price, qty)
        new_SL_order_id = new_stoploss_order.get('algoId')
    assert new_SL_order_id is not None, f"Could not get the new SL order ID for order: {new_stoploss_order}"
    db.insertNewCandle(json.dumps(candle_price), new_SL_order_id, group_id, order_enriched['candle_data']['trade_metadata'], order_enriched['candle_data']['actual_entry_price'])
    logging.info(f"✅ Successfully adjusted SL for order: {order_id}. New SL order: {new_SL_order_id}")

def check_for_SL_adjustment(order_enriched, close_price) -> bool: #TO-DO
    logging.info("Checking whether SL orders hit close price with params: ")
    logging.info(f'order_enriched: {order_enriched}')
    logging.info(f'close_price: {close_price}')
    adjustment = False
    direction = order_enriched['direction']
    if direction == "LONG":
        if float(close_price) > float(order_enriched['order_group_data']['trailing_price']):
            logging.info(f"✅ SL Adjustment will be made. [{direction}] Close Price:{float(close_price)} > trailing price:{float(order_enriched['order_group_data']['trailing_price'])}")
            adjustment = True
    elif direction == "SHORT":
        if float(close_price) < float(order_enriched['order_group_data']['trailing_price']):
            logging.info(f"✅ SL Adjustment will be made. [{direction}] Close Price:{float(close_price)} < trailing price:{float(order_enriched['order_group_data']['trailing_price'])}")
            adjustment = True
    if not adjustment:
        logging.info(f"😉 No trades need to be adjusted. [{direction}] Close Price:{float(close_price)}, trailing price:{float(order_enriched['order_group_data']['trailing_price'])}")
    return adjustment
