import os
import requests
from dotenv import load_dotenv

# Load the exact same keys we just tested
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

class Database:
    def __init__(self):
        self.endpoint = f"{SUPABASE_URL}/rest/v1/logs"
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

    def log_action(self, message: str, sentiment: str = "NEUTRAL"):
        """Sends a live log to the Vercel Dashboard"""
        data = {
            "message": message,
            "sentiment": sentiment
        }
        try:
            requests.post(self.endpoint, json=data, headers=self.headers)
        except Exception as e:
            print(f"Failed to push log to dashboard: {e}")

# Create a single instance to be used across the bot
db = Database()