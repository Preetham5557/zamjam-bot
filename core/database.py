import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def log_to_dashboard(message, sentiment="INFO"):
    """Sends a text status update to the React dashboard."""
    data = {"message": message, "sentiment": sentiment}
    supabase.table("logs").insert(data).execute()

def record_trade(symbol, side, price, qty):
    """Records a completed trade to the React dashboard."""
    data = {
        "symbol": symbol,
        "side": side,
        "price": float(price),
        "qty": int(qty)
    }
    supabase.table("trades").insert(data).execute()