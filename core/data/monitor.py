import os
from pathlib import Path
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

# Find the vault (.env) at the root
base_dir = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=base_dir / '.env')

def check_market_health():
    api = tradeapi.REST(
        os.getenv('APCA_API_KEY_ID'),
        os.getenv('APCA_API_SECRET_KEY'),
        os.getenv('APCA_API_BASE_URL'),
        api_version='v2'
    )
    
    try:
        # 1. Check Market Clock
        clock = api.get_clock()
        status = "OPEN" if clock.is_open else "CLOSED"
        
        # 2. Check Account Health
        account = api.get_account()
        
        print(f"--- {os.getenv('AGENT_NAME', 'Zamjam')} PRE-FLIGHT CHECK ---")
        print(f"Market is currently: {status}")
        print(f"Next Opening: {clock.next_open.strftime('%Y-%m-%d %H:%M')}")
        print(f"Next Closing: {clock.next_close.strftime('%Y-%m-%d %H:%M')}")
        print("-" * 35)
        print(f"Equity: ${account.equity}")
        print(f"Buying Power: ${account.buying_power}")
        print(f"Daytrade Count: {account.daytrade_count}/3")
        print("-" * 35)

    except Exception as e:
        print(f"❌ Monitor Error: {e}")

if __name__ == "__main__":
    check_market_health()