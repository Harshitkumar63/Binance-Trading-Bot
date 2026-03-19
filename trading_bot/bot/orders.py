from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.client import get_client
from bot.logging_config import setup_logging
from bot.validators import validate_cancel_payload, validate_order_payload

logger = setup_logging()


def format_binance_error(exc):
    if isinstance(exc, BinanceAPIException):
        code = getattr(exc, "code", None)
        message = getattr(exc, "message", None) or str(exc)
        status = getattr(exc, "status_code", None)
        parts = []
        if status is not None:
            parts.append(f"status={status}")
        if code is not None:
            parts.append(f"code={code}")
        meta = f" ({', '.join(parts)})" if parts else ""
        return f"{message}{meta}"

    return str(exc)


def _compute_avg_price(order_details):
    avg_price = order_details.get("avgPrice") or order_details.get("price")
    if avg_price not in (None, "0", 0):
        return avg_price

    executed_qty = order_details.get("executedQty")
    cum_quote = order_details.get("cumQuote")
    try:
        if executed_qty and float(executed_qty) > 0 and cum_quote is not None:
            return str(float(cum_quote) / float(executed_qty))
    except (TypeError, ValueError, ZeroDivisionError):
        return "0"

    return "0"


def _fetch_order_details(client, symbol, order_id):
    try:
        details = client.futures_get_order(symbol=symbol, orderId=order_id)
    except (BinanceAPIException, BinanceRequestException) as exc:
        logger.error("Binance error on order details: %s", format_binance_error(exc))
        raise

    logger.info("Order details response: %s", details)
    return details


def place_order(payload):
    validated = validate_order_payload(payload)
    client = get_client()

    params = {
        "symbol": validated["symbol"],
        "side": validated["side"],
        "type": validated["type"],
        "quantity": validated["quantity"],
    }

    if validated["type"] == "LIMIT":
        params["price"] = validated["price"]
        params["timeInForce"] = "GTC"

    logger.info("Order request payload: %s", params)

    try:
        response = client.futures_create_order(**params)
        logger.info("Order create response: %s", response)
        order_id = response.get("orderId")
        order_details = _fetch_order_details(client, validated["symbol"], order_id)
    except (BinanceAPIException, BinanceRequestException) as exc:
        logger.error("Binance error on create: %s", format_binance_error(exc))
        raise

    status = order_details.get("status")
    avg_price = _compute_avg_price(order_details)
    message = None
    if status == "NEW":
        message = "Order placed successfully but waiting for price match."

    return {
        "orderId": order_details.get("orderId"),
        "status": status,
        "executedQty": order_details.get("executedQty"),
        "avgPrice": avg_price,
        "message": message,
    }


def get_recent_orders(limit=10):
    client = get_client()
    logger.info("Fetching recent orders with limit=%s", limit)
    try:
        orders = client.futures_get_all_orders(limit=limit)
    except (BinanceAPIException, BinanceRequestException) as exc:
        logger.error("Binance error on orders list: %s", format_binance_error(exc))
        raise

    logger.info("Recent orders response count: %s", len(orders))
    return orders


def cancel_order(payload):
    validated = validate_cancel_payload(payload)
    client = get_client()
    params = {"symbol": validated["symbol"], "orderId": validated["orderId"]}
    logger.info("Cancel order request payload: %s", params)

    try:
        response = client.futures_cancel_order(**params)
    except (BinanceAPIException, BinanceRequestException) as exc:
        logger.error("Binance error on cancel: %s", format_binance_error(exc))
        raise

    logger.info("Cancel order response: %s", response)
    return response
