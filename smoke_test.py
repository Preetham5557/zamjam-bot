import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def verify_connection():
    print("🚀 --- ZAMJAM CLOUD SMOKE TEST --- 🚀")
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    try:
        supabase = create_client(url, key)
        # Try a simple insert
        test_data = {"message": "Dependency test: SUCCESS", "sentiment": "INFO"}
        response = supabase.table("logs").insert(test_data).execute()
        
        print("✅ DATABASE: Connection Successful!")
        print(f"📡 DATA SENT: {response.data}")
    except Exception as e:
        print(f"❌ CONNECTION FAILED: {e}")
        print("\nTip: If it says 'ModuleNotFoundError', try: pip install supabase")

if __name__ == "__main__":
    verify_connection()
    