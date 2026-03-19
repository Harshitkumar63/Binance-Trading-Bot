# Binance Futures Testnet Trading Bot

## Setup

1. Ensure Python 3.10+ is installed.
2. Create and activate a virtual environment (recommended):

```
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Add your Binance Futures Testnet API keys in `config.py`.

## Run FastAPI Backend + UI

```
python -m uvicorn api.main:app --reload
```

Open http://127.0.0.1:8000 in your browser.

## Run CLI

Example MARKET order:

```
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

Example LIMIT order:

```
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 30000
```

## Run Examples

Fetch recent orders (UI):

- Start the server and open the UI at http://127.0.0.1:8000
- Use the Refresh button in the Recent Orders panel

Cancel an open order:

- Place a LIMIT order so it remains open
- Click Cancel on the order row in the Recent Orders table

## Assumptions

- You are using Binance Futures Testnet (USDT-M) and have testnet API keys.
- Symbols are valid for Binance USDT-M futures (e.g., BTCUSDT, ETHUSDT).
- Network access to https://testnet.binancefuture.com is available.

## Notes

- Logging is stored in `logs/app.log`.
- Orders are placed on Binance Futures Testnet (USDT-M).
