from src.services import binanceREST
from src.utils.supabase_client_post import log_into_supabase
import logging


def adjust_SL_orders(adjustment_orders):
    for order in adjustment_orders:
        logging.info(f"Attempting to adjust SL the following order: {order}")

        order_id = order['order_id']
        symbol = order['symbol']
        side = order['side']
        breakeven_price = order['order_group']['breakeven_price']
        qty = order['qty']
        group_id = order['order_group']['group_id']
        binanceREST.cancel_stop_market_orders(symbol, order_id)
        new_stoploss = None
        try:
            new_stoploss = binanceREST.set_stop_loss(symbol, side, breakeven_price, qty)
        except:
            logging.error("Attempting to retry set stop loss...")
            new_stoploss = binanceREST.set_stop_loss(symbol, side, breakeven_price, qty)
        if not new_stoploss:
            logging.error(f"❌ Did not manage to set stop loss for {order_id}, continue to next order.")
            continue
        stoploss_order_id = new_stoploss['orderId']
        direction = "LONG" if side == "SELL" else "SHORT"

        # Log new stop loss into Supabase       
        group_order_data = {
            "group_id": group_id,
            "order_id": stoploss_order_id,
            "type": "SL",
            "direction": direction,
            "breakeven_threshold": 0.00,
            "breakeven_price": 0.00
        }
        try:
            log_into_supabase(group_order_data)
            logging.info("NEW STOPLOSS Order logged to Supabase")
        
        except Exception as e:
            logging.error(f"Failed to log NEW STOPLOSS trade to Supabase: {e}")

def check_for_SL_adjustments(open_sl_orders, close_price) -> list: #TO-DO
    adjustments = []
    for order in open_sl_orders:
        direction = order['direction']
        if direction == "LONG":
            if close_price > order['order_group']['breakeven_threshold']:
                adjustments.append(order)
        elif direction == "SHORT":
            if close_price < order['order_group']['breakeven_threshold']:
                adjustments.append(order)
    # If direction is LONG, then 
    return adjustments