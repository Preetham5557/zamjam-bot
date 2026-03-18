import time
import sys
from datetime import datetime
from core.data.monitor import check_market_health
from core.data.historian import fetch_historical_data
from core.data.analyzer import analyze_trends
from core.strategy import generate_signal
from core.agents import place_order
import alpaca_trade_api as tradeapi
import os

def run_cycle():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔄 NEW CYCLE STARTING...")
    
    symbol = "NVDA"
    fetch_historical_data(symbol)
    analyze_trends()
    signal = generate_signal()
    
    if signal == "BUY":
        place_order(symbol, qty=1, side='buy')
    elif signal == "SELL":
        place_order(symbol, qty=1, side='sell')
    else:
        print(f"😴 Status: {signal}. No action taken.")

def start_bot():
    print("🚀 --- ZAMJAM LIVE MONITOR ACTIVE --- 🚀")
    
    # Initialize API to check clock inside the loop
    api = tradeapi.REST(
        os.getenv('APCA_API_KEY_ID'),
        os.getenv('APCA_API_SECRET_KEY'),
        os.getenv('APCA_API_BASE_URL'),
        api_version='v2'
    )

    try:
        while True:
            clock = api.get_clock()
            
            if clock.is_open:
                run_cycle()
                print("\n⏳ Sleeping for 60 seconds...")
                time.sleep(60) 
            else:
                print(f"💤 Market is CLOSED. Next open: {clock.next_open.strftime('%m-%d %H:%M')}")
                print("Checking again in 1 hour...")
                time.sleep(3600) # Sleep for 1 hour if closed
                
    except KeyboardInterrupt:
        print("\n🛑 Zamjam shutdown requested by user. Goodbye!")
        sys.exit()

if __name__ == "__main__":
    start_bot()