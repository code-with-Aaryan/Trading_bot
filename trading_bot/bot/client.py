"""
Binance Futures Testnet REST client.

Handles:
- HMAC-SHA256 request signing
- Timestamping & recvWindow
- HTTP session management with retries
- Structured logging of every request/response
- Clean exception wrapping
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
import urllib.parse
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .logging_config import get_logger, setup_logger

setup_logger("trading_bot")
logger = get_logger("trading_bot.client")

TESTNET_BASE_URL = "https://testnet.binancefuture.com"
RECV_WINDOW = 5000  # ms


class BinanceAPIError(Exception):
    def __init__(self, code: int, message: str, status_code: int = 0):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(f"[Binance {code}] {message}")


class BinanceNetworkError(Exception):
    """Raised on connection/timeout failures."""


class BinanceFuturesClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = TESTNET_BASE_URL,
        timeout: int = 10,
    ) -> None:
        if not api_key or not api_secret:
            raise ValueError("Both api_key and api_secret must be provided.")
        self._api_key = api_key
        self._api_secret = api_secret.encode()
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = self._build_session()
        self._session.headers.update({"X-MBX-APIKEY": self._api_key})

    def get_server_time(self) -> int:
        data = self._public_get("/fapi/v1/time")
        return data["serverTime"]

    def get_exchange_info(self, symbol: str | None = None) -> dict:
        params = {"symbol": symbol.upper()} if symbol else {}
        return self._public_get("/fapi/v1/exchangeInfo", params)

    def get_account(self) -> dict:
        return self._signed_get("/fapi/v2/account")

    def place_order(self, **params: Any) -> dict:
        str_params = {k: str(v) for k, v in params.items() if v is not None}
        return self._signed_post("/fapi/v1/order", str_params)

    def get_order(self, symbol: str, order_id: int) -> dict:
        return self._signed_get("/fapi/v1/order", {"symbol": symbol, "orderId": order_id})

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        return self._signed_delete("/fapi/v1/order", {"symbol": symbol, "orderId": order_id})

    # ------------------------------------------------------------------
    def _public_get(self, path: str, params: dict | None = None) -> dict:
        url = self._base_url + path
        logger.debug("PUBLIC GET %s params=%s", url, params)
        try:
            resp = self._session.get(url, params=params or {}, timeout=self._timeout)
        except requests.exceptions.RequestException as exc:
            raise BinanceNetworkError(str(exc)) from exc
        return self._handle_response(resp, "GET", url)

    def _signed_get(self, path: str, params: dict | None = None) -> dict:
        url = self._base_url + path
        signed = self._sign(params or {})
        logger.debug("SIGNED GET %s params=%s", url, {k: v for k, v in signed.items() if k != "signature"})
        try:
            resp = self._session.get(url, params=signed, timeout=self._timeout)
        except requests.exceptions.RequestException as exc:
            raise BinanceNetworkError(str(exc)) from exc
        return self._handle_response(resp, "GET", url)

    def _signed_post(self, path: str, params: dict) -> dict:
        url = self._base_url + path
        signed = self._sign(params)
        log_params = {k: v for k, v in signed.items() if k != "signature"}
        logger.debug("SIGNED POST %s body=%s", url, log_params)
        try:
            resp = self._session.post(url, data=signed, timeout=self._timeout)
        except requests.exceptions.RequestException as exc:
            raise BinanceNetworkError(str(exc)) from exc
        return self._handle_response(resp, "POST", url)

    def _signed_delete(self, path: str, params: dict) -> dict:
        url = self._base_url + path
        signed = self._sign(params)
        logger.debug("SIGNED DELETE %s params=%s", url, {k: v for k, v in signed.items() if k != "signature"})
        try:
            resp = self._session.delete(url, params=signed, timeout=self._timeout)
        except requests.exceptions.RequestException as exc:
            raise BinanceNetworkError(str(exc)) from exc
        return self._handle_response(resp, "DELETE", url)

    def _sign(self, params: dict) -> dict:
        params = dict(params)
        params["timestamp"] = int(time.time() * 1000)
        params["recvWindow"] = RECV_WINDOW
        query = urllib.parse.urlencode(params)
        sig = hmac.new(self._api_secret, query.encode(), hashlib.sha256).hexdigest()
        params["signature"] = sig
        return params

    @staticmethod
    def _build_session() -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        return session

    def _handle_response(self, resp: requests.Response, method: str, url: str) -> dict:
        logger.debug("RESPONSE %s %s → HTTP %s | body=%s", method, url, resp.status_code, resp.text[:500])
        try:
            data = resp.json()
        except json.JSONDecodeError:
            raise BinanceNetworkError(f"Non-JSON response (HTTP {resp.status_code}): {resp.text[:200]}")

        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            raise BinanceAPIError(
                code=data.get("code", 0),
                message=data.get("msg", "Unknown error"),
                status_code=resp.status_code,
            )
        if not resp.ok:
            raise BinanceAPIError(code=resp.status_code, message=resp.text[:200], status_code=resp.status_code)
        return data
