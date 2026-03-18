import os
from pathlib import Path
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

# Setup pathing
base_dir = Path(__file__).resolve().parent.parent.parent
env_path = base_dir / '.env'
load_dotenv(dotenv_path=env_path)

def check_zamjam_connection():
    key_id = os.getenv('APCA_API_KEY_ID')
    secret_key = os.getenv('APCA_API_SECRET_KEY')
    base_url = os.getenv('APCA_API_BASE_URL')

    # --- DEBUG SECTION ---
    print(f"--- ZAMJAM DEBUGGER ---")
    if key_id:
        print(f"Key ID: {key_id[:5]}... (Length: {len(key_id)})")
    if secret_key:
        # We don't print the secret for safety, just the length
        print(f"Secret Length: {len(secret_key)} characters")
    print(f"URL: {base_url}")
    print(f"----------------------")

    if not key_id or not secret_key:
        print("❌ Error: Keys missing from .env")
        return

    api = tradeapi.REST(key_id, secret_key, base_url, api_version='v2')
    
    try:
        account = api.get_account()
        print(f"🚀 ZAMJAM ONLINE | Cash: ${account.cash}")
    except Exception as e:
        print(f"❌ Alpaca Error: {e}")

if __name__ == "__main__":
    check_zamjam_connection()