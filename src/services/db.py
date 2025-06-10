
from dotenv import load_dotenv
from src.utils.supabase_client import get_supabase_client
import logging
from datetime import datetime

load_dotenv()
supabase = get_supabase_client()

def get_open_SL_orders():
    """Returns open SL orders with their groups info in 'order_groups' field. """
    try:
        res = (
            supabase.table("orders")
            .select("*, order_groups(*)")
            .eq("order_type", "STOP_ORDER")
            .eq("status", "NEW")
            .execute()
        )
        return res
    except Exception as e: 
        print("There's an issue getting one order from supabase: ", e)
