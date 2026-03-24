import os
import numpy as np
import requests
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
from dotenv import load_dotenv

load_dotenv()
APCA_API_KEY = os.environ.get("APCA_API_KEY_ID")
APCA_API_SECRET = os.environ.get("APCA_API_SECRET_KEY")

# 1. Fetch Historical Crypto Data from Alpaca v1beta3 Endpoint
def get_crypto_data(symbol="BTC/USD", limit=8000):
    print(f"📊 Downloading historical data for {symbol}...")
    
    # We use 1-Hour bars to capture crypto's unique intraday volatility
    start_date = "2023-01-01T00:00:00Z"
    
    url = f"https://data.alpaca.markets/v1beta3/crypto/us/bars?symbols={symbol}&timeframe=1Hour&start={start_date}&limit={limit}"
    headers = {
        "APCA-API-KEY-ID": APCA_API_KEY,
        "APCA-API-SECRET-KEY": APCA_API_SECRET,
        "accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    if 'bars' not in data or symbol not in data['bars']:
        print(f"❌ API Error: {data}")
        return np.array([])
        
    close_prices = [bar['c'] for bar in data['bars'][symbol]]
    print(f"✅ Downloaded {len(close_prices)} hourly market bars.")
    
    return np.array(close_prices)

# 2. Build the Gym Environment (Identical architecture to your live bot)
class ZamjamTrainEnv(gym.Env):
    def __init__(self, prices):
        super(ZamjamTrainEnv, self).__init__()
        self.prices = prices
        self.current_step = 0
        self.window_size = 15
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(17,), dtype=np.float32)
        self.current_position = 0
        self.entry_price = 0.0

    def reset(self, seed=None):
        self.current_step = self.window_size
        self.current_position = 0
        self.entry_price = 0.0
        return self._get_obs(), {}

    def _get_obs(self):
        window_prices = self.prices[self.current_step - self.window_size : self.current_step]
        normalized = (window_prices - np.mean(window_prices)) / (np.std(window_prices) + 1e-8)
        unrealized_pnl = 0.0
        if self.current_position > 0:
            current_price = self.prices[self.current_step]
            unrealized_pnl = (current_price - self.entry_price) / self.entry_price
        state = np.append(normalized, [self.current_position, unrealized_pnl])
        return state.astype(np.float32)

    def step(self, action):
        current_price = self.prices[self.current_step]
        reward = 0.0
        if action == 2 and self.current_position > 0:
            reward = ((current_price - self.entry_price) / self.entry_price) * 100
            self.current_position = 0
            self.entry_price = 0.0
        elif action == 1 and self.current_position == 0:
            reward = -0.01 
            self.current_position = 1
            self.entry_price = current_price
        elif action == 0 and self.current_position > 0:
            reward = ((current_price - self.entry_price) / self.entry_price) * 10

        self.current_step += 1
        done = self.current_step >= len(self.prices) - 1
        obs = self._get_obs() if not done else np.zeros(17, dtype=np.float32)
        return obs, reward, done, False, {}

if __name__ == "__main__":
    historical_prices = get_crypto_data("BTC/USD", 8000)
    env = ZamjamTrainEnv(historical_prices)
    
    print("🧠 Initializing PPO Neural Network...")
    model = PPO("MlpPolicy", env, verbose=1)
    
    print("🏋️‍♂️ Training Zamjam Crypto Brain...")
    model.learn(total_timesteps=100000)
    
    os.makedirs("models", exist_ok=True)
    # Save this specific brain as ppo_btc.zip
    model.save("models/ppo_btc")
    print("🚀 Training complete! Brain saved to models/ppo_btc.zip")