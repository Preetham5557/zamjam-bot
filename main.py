import os
import time
import requests
import threading
from flask import Flask
from dotenv import load_dotenv

# Import our custom modules
from core.database import db
from core.strategy import strategy

load_dotenv()

# --- THE CLOUD HACK (Flask Web Server) ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "🤖 Zamjam Trading Matrix is online and executing."

def run_server():
    # Render dynamically assigns a port. We must bind to it.
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- ALPACA API ---
APCA_API_KEY = os.environ.get("APCA_API_KEY_ID")
APCA_API_SECRET = os.environ.get("APCA_API_SECRET_KEY")

HEADERS = {
    "APCA-API-KEY-ID": APCA_API_KEY,
    "APCA-API-SECRET-KEY": APCA_API_SECRET,
    "accept": "application/json"
}

def get_latest_price(symbol: str) -> float:
    if "/" in symbol:
        url = f"https://data.alpaca.markets/v1beta3/crypto/us/latest/trades?symbols={symbol}"
    else:
        url = f"https://data.alpaca.markets/v2/stocks/trades/latest?symbols={symbol}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        return data["trades"][symbol]["p"]
    except Exception as e:
        error_msg = f"Data Fetch Error for {symbol}: {e}"
        print(error_msg)
        # 🚨 THE NEW TWEAK: Send the error straight to your Vercel dashboard
        db.log_action(error_msg, "BEARISH") 
        return 0.0

# --- THE MAIN BRAIN ---
def run_trading_loop(target_symbol: str = "BTC/USD"):
    # Wait a few seconds to let the web server boot up first
    time.sleep(3)
    print(f"🤖 Zamjam is online. Monitoring {target_symbol}...")
    db.log_action("Cloud deployment verified. Trading loop engaged.", "SUCCESS")
    
    while True:
        try:
            current_price = get_latest_price(target_symbol)
            if current_price > 0:
                analysis = strategy.evaluate(target_symbol, current_price)
                log_msg = f"[{target_symbol}] {analysis['decision']} - {analysis['reason']}"
                print(log_msg)
                db.log_action(log_msg, analysis['sentiment'])
            
            time.sleep(15)
            
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    # 1. Start the Flask web server in a background thread to keep Render happy
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # 2. Start the actual AI trading loop
    run_trading_loop("BTC/USD")