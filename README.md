 Trading Bot 🚀

A clean, production-structured Python CLI bot for placing orders on Binance USDT-M Futures Testnet. Designed with modular architecture, logging, validation, and clear error handling.

✨ Features
✅ Market Orders (BUY / SELL)
✅ Limit Orders
✅ Stop-Market Orders
✅ Structured Logging (console + file)
✅ Input Validation
✅ Exception Handling (API / Network / Validation)
✅ .env Credential Support
✅ Modular Clean Code Structure

## 📂 Easy Project Structure

```bash
trading_bot/
├── main.py              # Run bot
├── config.py            # API keys & settings
├── bot.py               # Trading functions
├── utils.py             # Helper functions
├── logs.txt             # Logs file
├── requirements.txt     # Libraries
└── README.md            # Project info



⚙️ Installation
1️⃣ Clone Project
git clone https://github.com/yourusername/trading_bot.git
cd trading_bot
2️⃣ Create Virtual Environment
python -m venv .venv
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
3️⃣ Install Requirements
pip install -r requirements.txt

🔑 Setup API Credentials

Create .env

API_KEY=your_binance_key
API_SECRET=your_binance_secret
▶️ Usage
Market Buy
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
Limit Sell
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 100000
Stop Market Buy
python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 85000

🛡 Validation Examples
# Invalid side
python cli.py --side HOLD
# Error: Side invalid

# Quantity zero
python cli.py --quantity 0
# Error: Quantity must be > 0

📝 Logging

Logs automatically stored:

logs/trading_bot_YYYYMMDD.log

Each log contains:

Timestamp
Log Level
Module Name
Action Details

🧠 Tech Stack
Python
Requests
Binance Futures API
dotenv
argparse
Logging Module

📌 Best Use Cases
Binance Futures API Practice
Testnet Algo Bot Learning
Python CLI Projects
API Integration Portfolio Project
Internship Resume Project

🚀 Future Improvements
Web Dashboard (Flask / FastAPI)
Telegram Alerts
Auto TP/SL
Strategy Engine
Live Price Feed
Backtesting System

Built for learning professional crypto trading bot architecture using Python.
