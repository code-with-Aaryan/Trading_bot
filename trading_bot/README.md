# Binance Futures Testnet — Trading Bot

A clean, production-structured Python CLI for placing orders on the **Binance USDT-M Futures Testnet**.

---

## Features

| Feature | Status |
|---|---|
| Market orders (BUY / SELL) | ✅ |
| Limit orders (BUY / SELL) | ✅ |
| Stop-Market orders *(bonus)* | ✅ |
| Structured logging (file + console) | ✅ |
| Input validation with clear error messages | ✅ |
| Exception handling (API / network / validation) | ✅ |
| `.env` credential support | ✅ |

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # BinanceFuturesClient — API layer
│   ├── orders.py          # Order placement logic + OrderResult dataclass
│   ├── validators.py      # Input validation helpers
│   └── logging_config.py  # Structured file + console logging
├── cli.py                 # CLI entry point (argparse)
├── logs/                  # Auto-created; one log file per day
├── .env.example           # Credential template
├── requirements.txt
└── README.md
```

---

## Setup

### 1 — Get Testnet credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com) and log in with GitHub.
2. Click **API Key** → **Generate** and copy the key + secret.

### 2 — Clone / download the project

```bash
git clone https://github.com/<your-handle>/trading-bot.git
cd trading-bot
```

### 3 — Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4 — Configure credentials

```bash
cp .env.example .env
# Edit .env and fill in your API_KEY and API_SECRET
```

Your `.env` file should look like:

```
API_KEY=abc123...
API_SECRET=xyz789...
```

> Credentials can also be passed directly with `--api-key` / `--api-secret`, but using `.env` is recommended.

---

## How to Run

### Market BUY

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**Output:**

```
╔══════════════════════════════════════════════════╗
║   Binance Futures Testnet — Trading Bot v1.0     ║
╚══════════════════════════════════════════════════╝

────────────────────────────────────────────────────
  ORDER REQUEST SUMMARY
────────────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
────────────────────────────────────────────────────

  ✓ ORDER PLACED SUCCESSFULLY
────────────────────────────────────────────────────
  ORDER RESPONSE DETAILS
────────────────────────────────────────────────────
  Order ID        : 4429920965
  Client Order ID : x-xcKtGhcub6b3be3d0e
  Symbol          : BTCUSDT
  Side            : BUY
  Type            : MARKET
  Status          : FILLED
  Orig Qty        : 0.001
  Executed Qty    : 0.001
  Avg Price       : 93412.50000
────────────────────────────────────────────────────
```

---

### Limit SELL

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 100000
```

---

### Limit BUY with custom Time-in-Force

```bash
python cli.py --symbol ETHUSDT --side BUY --type LIMIT --quantity 0.01 --price 3000 --tif IOC
```

---

### Stop-Market BUY *(bonus order type)*

```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 85000
```

---

### Debug logging to console

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --log-level DEBUG
```

---

## Validation Examples

The CLI validates all inputs and prints clear error messages before touching the API:

```bash
# Missing price for LIMIT order
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001
# ✗ VALIDATION ERROR: Price is required for LIMIT orders.

# Invalid side
python cli.py --symbol BTCUSDT --side HODL --type MARKET --quantity 0.001
# ✗ VALIDATION ERROR: Side 'HODL' is invalid. Choose from: BUY, SELL.

# Zero quantity
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0
# ✗ VALIDATION ERROR: Quantity must be greater than zero, got 0.
```

---

## Logging

Logs are written to `logs/trading_bot_YYYYMMDD.log` (one file per day).

Each line includes timestamp, level, module name, and a structured message:

```
2025-04-22 10:15:01 | INFO     | trading_bot.client | BinanceFuturesClient initialised (testnet: https://testnet.binancefuture.com)
2025-04-22 10:15:01 | DEBUG    | trading_bot.client | ORDER REQUEST params={"symbol": "BTCUSDT", "side": "BUY", "type": "MARKET", "quantity": "0.001"}
2025-04-22 10:15:02 | DEBUG    | trading_bot.client | ORDER RESPONSE {"orderId": 4429920965, "status": "FILLED", ...}
2025-04-22 10:15:02 | INFO     | trading_bot.orders | MARKET order placed | orderId=4429920965 status=FILLED executedQty=0.001 avgPrice=93412.50000
```

Sample log files are included in the `logs/` directory.

---

## Assumptions

- **Testnet only.** The base URL is hard-coded to `https://testnet.binancefuture.com`. Switching to mainnet requires changing `TESTNET_BASE_URL` in `bot/client.py` and using live credentials.
- **Hedge mode not supported.** All orders use `positionSide=BOTH` (one-way mode), which is the testnet default.
- **Precision.** Quantity and price are passed as strings derived from user input. If Binance rejects due to lot-size / tick-size filters, adjust values to match the symbol's `LOT_SIZE` and `PRICE_FILTER` rules.
- **Python 3.10+** is recommended; minimum is 3.8 (f-strings, dataclasses, `from __future__ import annotations`).

---

## Requirements

```
binance-futures-connector>=3.3.0
python-dotenv>=1.0.0
```

Install: `pip install -r requirements.txt`

---

## License

MIT
