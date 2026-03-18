import pandas as pd
from pathlib import Path

# Paths
base_dir = Path(__file__).resolve().parent.parent
data_path = base_dir / 'core' / 'data' / 'NVDA_analyzed.csv'

def generate_signal():
    print(f"--- ⚡ Zamjam Strategy Engine ---")
    
    # 1. Load the analyzed data
    df = pd.read_csv(data_path, index_col=0)
    latest = df.iloc[-1]
    
    price = latest['close']
    sma5 = latest['SMA_5']
    sma10 = latest['SMA_10']
    
    # 2. Strategy Logic: "The Golden Pullback"
    # We want to buy ONLY if:
    # A) The short trend is above the long trend (SMA5 > SMA10)
    # B) The price is starting to bounce back above the SMA5
    
    signal = "HOLD"
    reason = "Waiting for better entry"

    if sma5 > sma10:
        if price > sma5:
            signal = "BUY"
            reason = "Price is trending up above averages (Bullish Confirmation)"
        else:
            signal = "WATCH"
            reason = "Averages are positive, but price is currently dipping below SMA_5"
    elif price < sma10:
        signal = "SELL / AVOID"
        reason = "Price is below major trend lines"

    print(f"Decision: {signal}")
    print(f"Reason:   {reason}")
    print(f"Details:  Price(${price:.2f}) | SMA5(${sma5:.2f}) | SMA10(${sma10:.2f})")
    
    return signal

if __name__ == "__main__":
    generate_signal()