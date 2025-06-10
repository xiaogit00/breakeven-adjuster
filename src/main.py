import logging, asyncio
from src.services import db
from src.services import binanceWebsocket 
from src.utils.logger import init_logger
from src.utils.calcs import check_for_SL_adjustments
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
        adjustments = check_for_SL_adjustments(open_SL_trades, close_price) #TO-DO
        execution_status = execution_data = None
        retry_count = 0
        if adjustments:
            while execution_status != ExecutionStatus.COMPLETE:
                if retry_count > 10: 
                    print("Too many retries, stopping Breakeven Adjuster service and exiting program.")
                    return
                try:
                    retry_count += 1
                    execution_status, execution_data = binanceAPI.adjust_SL(adjustments) # TO-DO
                except Exception as e: 
                    logging.info("An error occurred making adjustments: ", e)
        logging.info("🚀 SL adjustments complete!")
 




asyncio.run(main())

