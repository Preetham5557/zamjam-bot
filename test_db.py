import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def test_rest_connection():
    print("🚀 Bypassing dependency hell... connecting via direct REST API!")
    
    # The direct endpoint for your 'logs' table
    endpoint = f"{SUPABASE_URL}/rest/v1/logs"
    
    # Supabase requires these exact headers for REST auth
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal" # Tells Supabase not to send the whole row back
    }
    
    data = {
        "message": "Zamjam has bypassed the matrix! REST API is online.",
        "sentiment": "SUCCESS"
    }
    
    try:
        response = requests.post(endpoint, json=data, headers=headers)
        response.raise_for_status() # Throws an error if the status code is 4xx or 5xx
        print("✅ SUCCESS! Check your live Vercel Dashboard.")
    except Exception as e:
        print(f"❌ API CALL FAILED: {e}")
        # Print the exact error message from Supabase if it exists
        if 'response' in locals() and response.text:
            print(f"Supabase says: {response.text}")

if __name__ == "__main__":
    test_rest_connection()