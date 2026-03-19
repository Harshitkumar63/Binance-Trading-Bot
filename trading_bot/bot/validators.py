def validate_order_payload(payload):
    errors = []

    symbol = (payload.get("symbol") or "").strip().upper()
    side = (payload.get("side") or "").strip().upper()
    order_type = (payload.get("type") or "").strip().upper()

    quantity = payload.get("quantity")
    price = payload.get("price")

    if not symbol:
        errors.append("Symbol must not be empty")

    if side not in {"BUY", "SELL"}:
        errors.append("Side must be BUY or SELL")

    if order_type not in {"MARKET", "LIMIT"}:
        errors.append("Type must be MARKET or LIMIT")

    try:
        quantity = float(quantity)
        if quantity <= 0:
            errors.append("Quantity must be greater than 0")
    except (TypeError, ValueError):
        errors.append("Quantity must be a number")

    if order_type == "LIMIT":
        try:
            price = float(price)
            if price <= 0:
                errors.append("Price must be greater than 0")
        except (TypeError, ValueError):
            errors.append("Price is required for LIMIT orders")
    else:
        price = None

    if errors:
        raise ValueError("; ".join(errors))

    return {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
        "price": price,
    }


def validate_cancel_payload(payload):
    errors = []
    symbol = (payload.get("symbol") or "").strip().upper()
    order_id = payload.get("orderId")

    if not symbol:
        errors.append("Symbol must not be empty")

    try:
        order_id = int(order_id)
        if order_id <= 0:
            errors.append("Order ID must be greater than 0")
    except (TypeError, ValueError):
        errors.append("Order ID must be a number")

    if errors:
        raise ValueError("; ".join(errors))

    return {"symbol": symbol, "orderId": order_id}
