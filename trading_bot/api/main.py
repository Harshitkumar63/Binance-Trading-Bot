import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.logging_config import setup_logging
from bot.orders import cancel_order, format_binance_error, get_recent_orders, place_order

logger = setup_logging()
app = FastAPI(title="Binance Futures Testnet Trading Bot")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UI_DIR = os.path.join(BASE_DIR, "ui")

app.mount("/static", StaticFiles(directory=UI_DIR), name="static")


class OrderRequest(BaseModel):
    symbol: str
    side: str
    type: str
    quantity: float
    price: float | None = None


class CancelRequest(BaseModel):
    symbol: str
    orderId: int


@app.get("/")
def index():
    return FileResponse(f"{UI_DIR}/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/order")
def create_order(order: OrderRequest):
    payload = order.dict()
    logger.info("API order request: %s", payload)

    try:
        result = place_order(payload)
        logger.info("API order response: %s", result)
        return result
    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))
    except (BinanceAPIException, BinanceRequestException) as exc:
        error_message = format_binance_error(exc)
        logger.error("Binance API error: %s", error_message)
        raise HTTPException(status_code=502, detail=error_message)
    except Exception as exc:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/orders")
def list_orders():
    logger.info("API orders request")
    try:
        orders = get_recent_orders(limit=10)
        return {"orders": orders}
    except (BinanceAPIException, BinanceRequestException) as exc:
        error_message = format_binance_error(exc)
        logger.error("Binance API error: %s", error_message)
        raise HTTPException(status_code=502, detail=error_message)
    except Exception:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/cancel-order")
def cancel_order_endpoint(cancel: CancelRequest):
    payload = cancel.dict()
    logger.info("API cancel order request: %s", payload)

    try:
        result = cancel_order(payload)
        logger.info("API cancel order response: %s", result)
        return result
    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))
    except (BinanceAPIException, BinanceRequestException) as exc:
        error_message = format_binance_error(exc)
        logger.error("Binance API error: %s", error_message)
        raise HTTPException(status_code=502, detail=error_message)
    except Exception:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail="Internal server error")
