import pandas as pd
from pathlib import Path

# Path to your saved data
base_dir = Path(__file__).resolve().parent.parent.parent
data_path = base_dir / 'core' / 'data' / 'NVDA_history.csv'

def analyze_trends():
    print("--- 🧠 Zamjam is Analyzing NVDA ---")
    
    # 1. Load the data
    df = pd.read_csv(data_path, index_col=0)
    
    # 2. Calculate Moving Averages (The "Brain" Logic)
    # SMA_5: Average price of the last 5 days
    df['SMA_5'] = df['close'].rolling(window=5).mean()
    # SMA_10: Average price of the last 10 days
    df['SMA_10'] = df['close'].rolling(window=10).mean()
    
    # 3. Simple Signal Logic
    # If the current price is above the 5-day average, we'll call it 'Bullish'
    latest = df.iloc[-1]
    status = "BULLISH 📈" if latest['close'] > latest['SMA_5'] else "BEARISH 📉"
    
    print(f"Latest Close: ${latest['close']:.2f}")
    print(f"5-Day Average: ${latest['SMA_5']:.2f}")
    print(f"Market Sentiment: {status}")
    
    # 4. Save the analyzed data
    output_path = base_dir / 'core' / 'data' / 'NVDA_analyzed.csv'
    df.to_csv(output_path)
    print(f"\n✅ Analysis saved to: {output_path}")

if __name__ == "__main__":
    analyze_trends()