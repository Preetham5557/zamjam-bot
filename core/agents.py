import os
from pathlib import Path
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

# Load Vault
base_dir = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=base_dir / '.env')

def get_position_qty(api, symbol):
    """Returns the number of shares currently held for a symbol."""
    try:
        position = api.get_position(symbol)
        return int(position.qty)
    except Exception:
        # Alpaca throws an error if the position doesn't exist (0 shares)
        return 0

def place_order(symbol, qty, side='buy'):
    print(f"--- 🚀 {os.getenv('AGENT_NAME', 'Zamjam')} Execution Engine ---")
    
    api = tradeapi.REST(
        os.getenv('APCA_API_KEY_ID'),
        os.getenv('APCA_API_SECRET_KEY'),
        os.getenv('APCA_API_BASE_URL'),
        api_version='v2'
    )
    
    # 1. CHECK INVENTORY
    current_qty = get_position_qty(api, symbol)
    print(f"Current Inventory for {symbol}: {current_qty} shares")

    # 2. DECISION LOGIC
    if side == 'buy' and current_qty > 0:
        print(f"✋ HOLD: You already own {current_qty} shares. Skipping duplicate buy.")
        return
    
    if side == 'sell' and current_qty == 0:
        print(f"✋ HOLD: You don't own any {symbol} to sell. Skipping.")
        return

    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type='market',
            time_in_force='gtc'
        )
        print(f"✅ SUCCESS: {side.upper()} order for {qty} shares submitted!")
    except Exception as e:
        print(f"❌ Execution Error: {e}")

if __name__ == "__main__":
    place_order("NVDA", 1)