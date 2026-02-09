
from dotenv import load_dotenv
from src.utils.supabase_client import get_supabase_client
import logging, os
from datetime import datetime
from typing import Optional

load_dotenv()
supabase = get_supabase_client()
orders_table = "orders"
order_groups_table = "order_groups"
trades_table = "trades"
candles_table = "candles"

def insertNewOrderByType(order_type, order_data):
    logging.info(f"✏️ Attempting to insert new order into DB... Order Type: {order_type}")
    logging.info(f"Order Data: {order_data}")
    try:
        newOrder = {
            "order_id":order_data["order_id"],
            "status":order_data["status"],
            "direction":order_data["direction"],
            "symbol":order_data["symbol"],
            "order_type":order_data["type"],
            "ask_price":None if order_data["type"] == "MARKET" else order_data["ask_price"], # Ask Price is none,
            "filled_price":None, # Filled Price Price is none
            "side":order_data["side"],
            "qty": order_data['qty'],
            "created_at": str(datetime.fromtimestamp(order_data["created_at"]/1000)),
            "updated_at": None,
        }
        res = (
            supabase.table(orders_table)
            .insert(newOrder)
            .execute()
        )
        return res
    except Exception as e: 
        print("There's an issue updating supabase table: ", e)

def get_latest_open_SL_order() -> dict | None:
    """Returns open SL orders with their groups info in 'order_group' field."""
    logging.info("Trying to get open SL orders from DB...")
    try:
        # Step 1: Fetch the only SL
        orders_resp = supabase.table(orders_table) \
            .select("*") \
            .eq("order_type", "STOP_MARKET") \
            .eq("status", "NEW") \
            .execute()
        orders = orders_resp.data or []
        logging.info(f"Response from Supabase:{orders}")
        if not orders:
            logging.info("No open SL orders found.")
            return None
        if len(orders) > 1:
            raise ValueError(
                f"More than 1 open SL order found. "
                f"Response: {orders_resp}"
            )
        if orders[0].get("order_id") == None:
            raise ValueError(
                f"Issue with fetching latest open orders, no order_id found for response:{orders_resp}"
            )
        order_data = orders[0]
        return order_data
    except ValueError as e:
        # For ValueError, log and re-raise (don't swallow it)
        logging.critical(f"ValueError in get_latest_open_SL_order: {e}")
        raise
    except Exception as e:
        logging.exception("Error retrieving latest open SL orders from Supabase")
        return None

def enrich_order(order) -> dict | None:
    '''Given an order (dict), enriches it with 2 more fields: "order_group_data" and "candle_data" by calling DB'''
    try:
        # Step 2: Fetch the order_group info for that SL order
        SL_order_id = order['order_id']
        groups_resp = supabase.table(order_groups_table) \
            .select("*") \
            .eq("order_id", SL_order_id) \
            .execute() 
        order_group = groups_resp.data or []
        if len(order_group) != 1:
            raise ValueError(
                f"Not exactly 1 order_groups order found. "
                f"order_group Response: {order_group}"
            )
        if order_group[0].get("order_id") == None:
            raise ValueError(
                f"Issue finding order_id field of order_group found for response:{order_group}"
            )
        order_group_data = order_group[0]
        logging.info(f"Successfully fetched order_group_data: {order_group_data}")
        # Step 3: Get the candle data for all these SL orders
        candles_resp = supabase.table(candles_table) \
            .select("*") \
            .eq("order_id", SL_order_id) \
            .execute() 
        order_candle = candles_resp.data or []
        if len(order_candle) != 1:
            raise ValueError(
                f"Not exactly 1 candle found. "
                f"order_candle Response: {order_candle}"
            )
        if order_candle[0].get("order_id") == None:
            raise ValueError(
                f"Issue finding order_id field of candle found for response:{order_candle}"
            )
        order_candle_data = order_candle[0]
        logging.info(f"Successfully fetched order_candle_data: {order_candle_data}")
        # Step 4: Map and merge
        order_enriched = {
            **order,
            "order_group_data": order_group_data,
            "candle_data": order_candle_data
        }

        logging.info(f"Returning enriched order data: {order_enriched}")
        return order_enriched
    except ValueError as e:
        # For ValueError, log and re-raise (don't swallow it)
        logging.critical(f"ValueError in enrich_order: {e}")
        raise
    except Exception as e:
        logging.exception("Error retrieving latest open SL orders from Supabase")
        return None
        

def insertNewCandle(candle_price, new_SL_order_id, group_id, trade_metadata, actual_entry_price):
    logging.info(f"OrderID: {new_SL_order_id} | Inserting candle data into candles table: {candle_price}")
    logging.info(f"Trade Metadata: {trade_metadata}")

    candle_data = {
        "order_id": new_SL_order_id,
        "group_id": group_id,
        "candle_data": candle_price,
        "trade_metadata": trade_metadata,
        "actual_entry_price": actual_entry_price
    }
    
    try:
        res = (
            supabase.table(candles_table)
            .insert(candle_data)
            .execute()
        )
        if res.data:
            logging.info(f"Successfully inserted new entry with order_id {new_SL_order_id} into order_group table.")
        return res
    except Exception as e: 
        print("There's an issue getting supabase table: ", e)



def delete_orders():
    """Delete all orders"""
    logging.info("Deleting all orders from DB...")
    try:
        res = (
            supabase.table(orders_table)
            .delete()
            .neq("order_id", 0)
            .execute()
        )
        return res
    except Exception as e: 
        print("There's an issue updating supabase table: ", e)

def delete_order_groups():
    """Delete all order groups"""
    try:
        res = (
            supabase.table(order_groups_table)
            .delete()
            .neq("order_id", 0)
            .execute()
        )
        return res
    except Exception as e: 
        print("There's an issue updating supabase table: ", e)

def delete_trades():
    """Delete all trades table"""
    try:
        res = (
            supabase.table(trades_table)
            .delete()
            .neq("group_id", 0)
            .execute()
        )
        return res
    except Exception as e: 
        print("There's an issue updating supabase table: ", e)

def delete_candles():
    """Delete all candles table"""
    try:
        res = (
            supabase.table(candles_table)
            .delete()
            .neq("group_id", 0)
            .execute()
        )
        return res
    except Exception as e: 
        print("There's an issue updating supabase table: ", e)

def insertNewOrderGroup(new_group_id, order_group_data) -> Optional[int]:
    logging.info(f"✏️ Trying to insert a new order_group record with params: {order_group_data}")
    try:
        res = (
            supabase.table(order_groups_table)
            .insert(order_group_data)
            .execute()
        )
        if res.data:
            logging.info(f"Successfully inserted new entry with group_id {new_group_id} into order_group table.")
        return res
    except Exception as e: 
        print("There's an issue getting supabase table: ", e)