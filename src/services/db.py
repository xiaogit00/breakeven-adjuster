
from dotenv import load_dotenv
from src.utils.supabase_client import get_supabase_client
import logging
from datetime import datetime

load_dotenv()
supabase = get_supabase_client()

def get_open_SL_orders():
    """Returns open SL orders with their groups info in 'order_groups' field. """
    try:
        orders_resp = supabase.table("orders") \
            .select("*") \
            .eq("order_type", "STOP_MARKET") \
            .eq("status", "NEW") \
            .execute()
        orders = orders_resp.data
        order_ids = list({order['order_id'] for order in orders})
        groups_resp = supabase.table("order_groups") \
        .select("*") \
        .in_("order_id", order_ids) \
        .execute()

        groups = groups_resp.data
        group_map = {g['order_id']: g for g in groups}
        orders_with_groups = [
            {**order, "order_group": group_map.get(order['order_id'])}
            for order in orders
        ]

        return orders_with_groups
    except Exception as e: 
        print("There's an issue getting one order from supabase: ", e)
