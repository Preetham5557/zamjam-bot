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

# 1. Fetch Historical Data from Alpaca
def get_historical_data(symbol="AAPL", limit=2000):
    print(f"📊 Downloading historical data for {symbol}...")
    
    # We must provide a start date, otherwise Alpaca only returns today's data.
    # 2016 gives us plenty of bull and bear markets to train on.
    start_date = "2016-01-01T00:00:00Z"
    
    url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbol}&timeframe=1Day&start={start_date}&limit={limit}"
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
        
    # Extract just the closing prices to train the matrix
    close_prices = [bar['c'] for bar in data['bars'][symbol]]
    print(f"✅ Downloaded {len(close_prices)} market days.")
    
    return np.array(close_prices)

# 2. Build the Gym Environment (Translating strategy.py for SB3)
class ZamjamTrainEnv(gym.Env):
    def __init__(self, prices):
        super(ZamjamTrainEnv, self).__init__()
        self.prices = prices
        self.current_step = 0
        self.window_size = 15
        
        # Action Space: 0=HOLD, 1=BUY, 2=SELL
        self.action_space = spaces.Discrete(3)
        
        # Observation Space: (17,) array matching our strategy.py exactly
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(17,), dtype=np.float32)
        
        self.current_position = 0
        self.entry_price = 0.0

    def reset(self, seed=None):
        self.current_step = self.window_size
        self.current_position = 0
        self.entry_price = 0.0
        return self._get_obs(), {}

    def _get_obs(self):
        # The exact same normalization matrix from your live bot
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
        
        # Reward shaping (Same as live environment)
        if action == 2 and self.current_position > 0: # SELL
            reward = ((current_price - self.entry_price) / self.entry_price) * 100
            self.current_position = 0
            self.entry_price = 0.0
        elif action == 1 and self.current_position == 0: # BUY
            reward = -0.01 # Minor slippage penalty
            self.current_position = 1
            self.entry_price = current_price
        elif action == 0 and self.current_position > 0: # HOLD
            reward = ((current_price - self.entry_price) / self.entry_price) * 10

        self.current_step += 1
        done = self.current_step >= len(self.prices) - 1
        
        obs = self._get_obs() if not done else np.zeros(17, dtype=np.float32)
        return obs, reward, done, False, {}

if __name__ == "__main__":
    historical_prices = get_historical_data("AAPL", 2000)
    env = ZamjamTrainEnv(historical_prices)
    
    print("🧠 Initializing PPO Neural Network...")
    model = PPO("MlpPolicy", env, verbose=1)
    
    print("🏋️‍♂️ Training Zamjam. Running 100,000 market simulations...")
    # This executes the gradient descent loop
    model.learn(total_timesteps=100000)
    
    # Save the finalized weights
    os.makedirs("models", exist_ok=True)
    model.save("models/ppo_zamjam")
    print("🚀 Training complete! Brain saved to models/ppo_zamjam.zip")