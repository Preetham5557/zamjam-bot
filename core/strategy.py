import os
import requests
import numpy as np
from collections import deque
from stable_baselines3 import PPO
from dotenv import load_dotenv

load_dotenv()

# Alpaca API Endpoints
APCA_API_KEY = os.environ.get("APCA_API_KEY_ID")
APCA_API_SECRET = os.environ.get("APCA_API_SECRET_KEY")
ORDER_URL = "https://paper-api.alpaca.markets/v2/orders"
ACCOUNT_URL = "https://paper-api.alpaca.markets/v2/account"

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
        
        # NEW: We need to remember exactly how much we bought, 
        # so we know exactly how much to sell later.
        self.last_trade_qty = 0.0 
        
        model_path = os.path.join("models", "ppo_btc.zip")
        if os.path.exists(model_path):
            self.model = PPO.load(model_path)
        else:
            print("⚠️ No trained model found. Zamjam will trade randomly.")
            self.model = None

    def _get_dynamic_qty(self, current_price: float) -> str:
        """Calculates order size based on 5% of total buying power."""
        try:
            # 1. Ask Alpaca how much money we have
            response = requests.get(ACCOUNT_URL, headers=HEADERS)
            response.raise_for_status()
            account_data = response.json()
            
            buying_power = float(account_data['buying_power'])
            
            # 2. Risk exactly 5% of available buying power per trade
            trade_value_usd = buying_power * 0.05 
            
            # 3. Calculate how much BTC that buys at the current live price
            qty = round(trade_value_usd / current_price, 5)
            
            # Failsafe: Ensure we never try to buy 0
            return str(max(qty, 0.0001))
            
        except Exception as e:
            print(f"⚠️ Account API Error, defaulting to small trade: {e}")
            return "0.001"

    def _submit_order(self, symbol: str, side: str, qty: str):
        """Sends a live Market Order to Alpaca with the dynamically calculated quantity."""
        data = {
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": "market",
            "time_in_force": "gtc"
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

        if self.model:
            action, _states = self.model.predict(state, deterministic=True)
            action = int(action)
        else:
            action = 0 

        sentiment = "NEUTRAL"
        decision = "HOLD"
        reason = f"Agent Action: {action} (HOLD). Monitoring trend."

        if action == 1 and self.current_position == 0:
            # AI says BUY. Calculate 5% of our bank account and buy that much.
            dynamic_qty = self._get_dynamic_qty(current_price)
            
            success = self._submit_order(symbol, "buy", dynamic_qty)
            if success:
                self.current_position = 1
                self.entry_price = current_price
                self.last_trade_qty = float(dynamic_qty) # Memorize the exact amount
                decision = "BUY"
                sentiment = "BULLISH"
                reason = f"Live Order: Bought {dynamic_qty} {symbol} at ${current_price:.2f} (5% of Buying Power)"
            else:
                reason = "Agent attempted BUY, but broker API rejected the order."

        elif action == 2 and self.current_position > 0:
            # AI says SELL. Fetch the memorized amount and liquidate it.
            sell_qty = str(self.last_trade_qty)
            
            success = self._submit_order(symbol, "sell", sell_qty)
            if success:
                profit = current_price - self.entry_price
                self.current_position = 0
                self.entry_price = 0.0
                self.last_trade_qty = 0.0 # Wipe the memory
                decision = "SELL"
                sentiment = "SUCCESS" if profit > 0 else "BEARISH"
                reason = f"Live Order Executed: Sold {sell_qty} {symbol}. PnL: ${profit:.2f}"
            else:
                reason = "Agent attempted SELL, but broker API rejected the order."

        return {
            "symbol": symbol, "decision": decision, "sentiment": sentiment,
            "reason": reason, "price": current_price
        }

strategy = RLTradingEnvironment()