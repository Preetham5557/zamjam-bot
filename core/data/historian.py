import os
from pathlib import Path
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import pandas as pd
from datetime import datetime, timedelta

# 1. SETUP PATHS
# Finds the .env file in the root 'zamjam' folder
base_dir = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=base_dir / '.env')

def fetch_historical_data(symbol):
    """
    Fetches daily bars for a symbol using the free IEX data feed.
    """
    api = tradeapi.REST(
        os.getenv('APCA_API_KEY_ID'),
        os.getenv('APCA_API_SECRET_KEY'),
        os.getenv('APCA_API_BASE_URL'),
        api_version='v2'
    )
    
    # 2. DEFINE DATE RANGE
    # Free accounts get the best results when requesting data older than 15 minutes.
    # We'll look at the last 30 days.
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    print(f"--- 📜 {os.getenv('AGENT_NAME', 'Zamjam')} Historian ---")
    print(f"Target: {symbol}")
    print(f"Source: IEX (Free Tier)")
    print(f"Range: {start_date} to {end_date}")
    
    try:
        # 3. THE API CALL
        # feed='iex' is the critical flag for free accounts
        bars = api.get_bars(
            symbol, 
            tradeapi.TimeFrame.Day, 
            start=start_date.isoformat(),
            end=end_date.isoformat(),
            adjustment='split',
            feed='iex' 
        ).df
        
        if bars.empty:
            print(f"⚠️ No data found. IEX might not have trades for {symbol} in this range.")
            return

        # 4. DATA CLEANING
        # Ensure the index is a simple date for easier reading
        bars.index = bars.index.date
        
        print(f"✅ Success! Retrieved {len(bars)} days of data.")
        print("-" * 35)
        print(bars[['close', 'volume']].tail(5)) # Show just the Close and Volume
        print("-" * 35)
        
        # 5. SAVE FOR AI TRAINING
        save_path = base_dir / 'core' / 'data' / f'{symbol}_history.csv'
        bars.to_csv(save_path)
        print(f"💾 File Saved: {save_path}")
        
    except Exception as e:
        print(f"❌ Historian Error: {e}")
        if "subscription" in str(e).lower():
            print("Tip: This usually means you tried to access SIP data without a Pro subscription.")

if __name__ == "__main__":
    # You can change this to any major stock like AAPL, TSLA, or MSFT
    fetch_historical_data("NVDA")