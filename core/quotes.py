import os
from pathlib import Path
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

# Find the vault (.env)
base_dir = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=base_dir / '.env')

def get_zamjam_quote(symbol):
    api = tradeapi.REST(
        os.getenv('APCA_API_KEY_ID'),
        os.getenv('APCA_API_SECRET_KEY'),
        os.getenv('APCA_API_BASE_URL'),
        api_version='v2'
    )
    
    try:
        # Fetch the latest trade (price) for the stock
        trade = api.get_latest_trade(symbol)
        print(f"\n📈 {os.getenv('AGENT_NAME', 'Zamjam')} MARKET REPORT")
        print(f"Ticker: {symbol}")
        print(f"Current Price: ${trade.price}")
        print(f"Timestamp: {trade.timestamp}\n")
    except Exception as e:
        print(f"❌ Zamjam couldn't find {symbol}: {e}")

if __name__ == "__main__":
    # Feel free to change "NVDA" to "AAPL" or "TSLA"
    get_zamjam_quote("NVDA")