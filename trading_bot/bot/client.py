"""
client.py — Low-level Binance Futures Testnet API client.
Handles authentication (HMAC-SHA256), request signing, and raw HTTP calls.
"""

import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logger

BASE_URL = "https://testnet.binancefuture.com"
logger = setup_logger("client")


class BinanceAPIError(Exception):
    """Raised when the Binance API returns an error response."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API error {code}: {message}")


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })

    # ── Signing ────────────────────────────────────────────────────────────────

    def _sign(self, params: Dict[str, Any]) -> str:
        query = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _server_time(self) -> int:
        """Fetch Binance server time to avoid clock-skew errors (-1021)."""
        try:
            resp = self.session.get(BASE_URL + "/fapi/v1/time", timeout=5)
            return resp.json()["serverTime"]
        except Exception:
            return int(time.time() * 1000)  # fallback to local time

    def _timestamp(self) -> int:
        return self._server_time()

    # ── Raw request ────────────────────────────────────────────────────────────

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        url = BASE_URL + path
        params = params or {}

        if signed:
            params["timestamp"] = self._timestamp()
            params["signature"] = self._sign(params)

        logger.debug("REQUEST  %s %s | params=%s", method.upper(), path, params)

        try:
            if method.upper() == "GET":
                resp = self.session.get(url, params=params, timeout=10)
            else:
                resp = self.session.post(url, data=params, timeout=10)
        except requests.exceptions.RequestException as exc:
            logger.error("Network error: %s", exc)
            raise ConnectionError(f"Network error communicating with Binance: {exc}") from exc

        logger.debug("RESPONSE %s | body=%s", resp.status_code, resp.text[:500])

        try:
            data = resp.json()
        except ValueError:
            logger.error("Non-JSON response: %s", resp.text[:200])
            raise BinanceAPIError(-1, f"Unexpected response: {resp.text[:200]}")

        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            logger.error("API error: code=%s msg=%s", data.get("code"), data.get("msg"))
            raise BinanceAPIError(data["code"], data.get("msg", "Unknown error"))

        return data

    # ── Public helpers ─────────────────────────────────────────────────────────

    def get_exchange_info(self) -> Dict[str, Any]:
        return self._request("GET", "/fapi/v1/exchangeInfo")

    def get_account(self) -> Dict[str, Any]:
        return self._request("GET", "/fapi/v2/account", signed=True)

    def place_order(self, **kwargs) -> Dict[str, Any]:
        return self._request("POST", "/fapi/v1/order", params=kwargs, signed=True)
