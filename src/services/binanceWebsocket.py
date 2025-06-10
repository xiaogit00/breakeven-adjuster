from dotenv import load_dotenv
import requests, os, asyncio, logging, websockets, json, time
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
baseUrl = 'https://fapi.binance.com'
listen_key = None

load_dotenv()

async def websocket_binance_price_listener(binance_price_queue: asyncio.Queue, interval=10):
    ws_url = f"wss://fstream.binance.com/ws/solusdt@ticker"
    logging.info(f"Connecting to {ws_url}")

    while True:
        try:
            async with websockets.connect(ws_url) as ws:
                logging.info(f"✅ Connected to Binance price listening websocket")
                last_print_time = 0
                while True:
                    try:
                        message = await ws.recv()
                        parsed = json.loads(message)
                        current_time = time.time()
                        if current_time - last_print_time >= interval:
                            last_print_time = current_time
                            await binance_price_queue.put(parsed)
                    except asyncio.TimeoutError:
                        logging.warning("⏱️ No message in 60 seconds. Sending ping...")
                        try:
                            pong = await ws.ping()
                            await asyncio.wait_for(pong, timeout=10)
                        except asyncio.TimeoutError:
                            logging.warning("⚠️ Ping timed out. Reconnecting...")
                            break  # Exit to reconnect

        except (ConnectionClosedError, ConnectionClosedOK) as e:
            logging.info(f"🔌 Binance event websocket closed: {e}. Reconnecting...")
        except Exception as e:
            logging.critical(f"🔥 Unexpected WebSocket error for Binance event websocket: {e}", exc_info=True)
        await asyncio.sleep(2)  # Optional: prevent rapid reconnect loop