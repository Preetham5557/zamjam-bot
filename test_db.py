import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

def test():
    print("🚀 Testing Supabase Connection...")
    try:
        supabase = create_client(url, key)
        data = {"message": "Zamjam is Live!", "sentiment": "SUCCESS"}
        supabase.table("logs").insert(data).execute()
        print("✅ SUCCESS! Check your Supabase Dashboard.")
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    test()
