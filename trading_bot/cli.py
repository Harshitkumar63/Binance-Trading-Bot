import argparse
import json
import sys

from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.logging_config import setup_logging
from bot.orders import place_order

logger = setup_logging()


def parse_args():
    parser = argparse.ArgumentParser(description="Binance Futures Testnet Trading Bot")
    parser.add_argument("--symbol", required=True, help="Trading symbol, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL"], help="BUY or SELL")
    parser.add_argument("--type", required=True, choices=["MARKET", "LIMIT"], help="Order type")
    parser.add_argument("--quantity", required=True, type=float, help="Order quantity")
    parser.add_argument("--price", type=float, help="Limit price")
    return parser.parse_args()


def main():
    args = parse_args()
    payload = {
        "symbol": args.symbol,
        "side": args.side,
        "type": args.type,
        "quantity": args.quantity,
        "price": args.price,
    }

    try:
        result = place_order(payload)
        print(json.dumps(result, indent=2))
    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        print(f"Validation error: {exc}")
        sys.exit(1)
    except (BinanceAPIException, BinanceRequestException) as exc:
        logger.error("Binance API error: %s", exc)
        print("Binance API error")
        sys.exit(2)
    except Exception:
        logger.exception("Unexpected error")
        print("Unexpected error")
        sys.exit(3)


if __name__ == "__main__":
    main()
