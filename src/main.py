import logging, asyncio
from src.services import db
from src.services import binanceWebsocket 
from src.utils.logger import init_logger
from src.utils import stoploss_adjuster
from src.utils.type_defs import ExecutionStatus

async def main():
    init_logger()
    binance_price_queue = asyncio.Queue()
    asyncio.create_task(binanceWebsocket.websocket_binance_price_listener(binance_price_queue)) # Creates a background task. 
    while True:
        new_price = await binance_price_queue.get()
        logging.info("🔴 Awaiting next event in queue from Binance event websocket...")
        logging.info(f"😱 Received new Binance event! Event: {new_price}")
        close_price = new_price['c']
        open_SL_trades = db.get_open_SL_orders() # Ref response in sample_api
        if not open_SL_trades: continue
        adjustment_orders = stoploss_adjuster.check_for_SL_adjustments(open_SL_trades, close_price)
        stoploss_adjuster.adjust_SL_orders(adjustment_orders)
        logging.info("🚀 SL adjustments complete!")
 

asyncio.run(main())

