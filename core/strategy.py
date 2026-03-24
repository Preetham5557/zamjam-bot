import os
import requests
import numpy as np
from collections import deque
from stable_baselines3 import PPO
from dotenv import load_dotenv

load_dotenv()

# Alpaca Paper Trading Credentials
APCA_API_KEY = os.environ.get("APCA_API_KEY_ID")
APCA_API_SECRET = os.environ.get("APCA_API_SECRET_KEY")
ORDER_URL = "https://paper-api.alpaca.markets/v2/orders"

HEADERS = {
    "APCA-API-KEY-ID": APCA_API_KEY,
    "APCA-API-SECRET-KEY": APCA_API_SECRET,
    "accept": "application/json",
    "content-type": "application/json"
}

class RLTradingEnvironment:
    def __init__(self):
        self.window_size = 15
        self.price_history = deque(maxlen=self.window_size)
        self.current_position = 0 
        self.entry_price = 0.0
        
        # Fixed order size for our paper trading test
        self.trade_qty = "0.001" 
        
        # Load the trained AI Brain
        # Load the trained AI Brain
        model_path = os.path.join("models", "ppo_btc.zip")
        if os.path.exists(model_path):
            self.model = PPO.load(model_path)
        else:
            print("⚠️ No trained model found. Zamjam will trade randomly.")
            self.model = None

    def _submit_order(self, symbol: str, side: str):
        """Sends a live Market Order to Alpaca."""
        data = {
            "symbol": symbol,
            "qty": self.trade_qty,
            "side": side,
            "type": "market",
            "time_in_force": "gtc" # Good 'Til Canceled
        }
        try:
            response = requests.post(ORDER_URL, json=data, headers=HEADERS)
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as err:
            print(f"❌ Order Failed: {response.text}")
            return False

    def get_state(self, current_price):
        self.price_history.append(current_price)
        if len(self.price_history) < self.window_size:
            return None 

        prices = np.array(self.price_history)
        normalized_prices = (prices - np.mean(prices)) / (np.std(prices) + 1e-8)

        unrealized_pnl = 0.0
        if self.current_position > 0:
            unrealized_pnl = (current_price - self.entry_price) / self.entry_price

        state_vector = np.append(normalized_prices, [self.current_position, unrealized_pnl])
        return state_vector.astype(np.float32)

    def evaluate(self, symbol: str, current_price: float) -> dict:
        state = self.get_state(current_price)

        if state is None:
            return {
                "symbol": symbol, "decision": "HOLD", "sentiment": "NEUTRAL",
                "reason": f"Populating state matrix: {len(self.price_history)}/{self.window_size}",
                "price": current_price
            }

        # --- AI INFERENCE ---
        if self.model:
            action, _states = self.model.predict(state, deterministic=True)
            # FORCE A BUY FOR TESTING: Uncomment the line below
            # action = 1 
        else:
            action = 0 

        # --- ACTION EXECUTION ---
        sentiment = "NEUTRAL"
        decision = "HOLD"
        reason = f"Agent Action: {action} (HOLD). Monitoring trend."

        if action == 1 and self.current_position == 0:
            # The AI wants to buy. Fire the API call.
            success = self._submit_order(symbol, "buy")
            if success:
                self.current_position = 1
                self.entry_price = current_price
                decision = "BUY"
                sentiment = "BULLISH"
                reason = f"Live Order Executed: Bought {self.trade_qty} {symbol} at ${current_price:.2f}"
            else:
                reason = "Agent attempted BUY, but broker API rejected the order."

        elif action == 2 and self.current_position > 0:
            # The AI wants to sell. Fire the API call.
            success = self._submit_order(symbol, "sell")
            if success:
                profit = current_price - self.entry_price
                self.current_position = 0
                self.entry_price = 0.0
                decision = "SELL"
                sentiment = "SUCCESS" if profit > 0 else "BEARISH"
                reason = f"Live Order Executed: Sold {symbol}. PnL: ${profit:.2f}"
            else:
                reason = "Agent attempted SELL, but broker API rejected the order."

        return {
            "symbol": symbol, "decision": decision, "sentiment": sentiment,
            "reason": reason, "price": current_price
        }

strategy = RLTradingEnvironment()