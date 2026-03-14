# Binance Futures Testnet Trading Bot

A lightweight Python CLI application for placing orders on **Binance Futures Testnet (USDT-M)**.

---

## Project Structure

```
trading_bot/
  bot/
    __init__.py
    client.py          # Binance API client (auth, signing, HTTP)
    orders.py          # Order placement logic
    validators.py      # Input validation
    logging_config.py  # Logging setup
  cli.py               # CLI entry point
  requirements.txt
  README.md
```

---

## Setup

### 1. Get Testnet Credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with your GitHub account
3. Generate API Key and Secret from the dashboard

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

```bash
export BINANCE_TESTNET_API_KEY="your_api_key"
export BINANCE_TESTNET_API_SECRET="your_api_secret"
```

Or pass them directly via flags (see examples below).

---

## Usage

```
python cli.py --symbol <SYMBOL> --side <BUY|SELL> --type <MARKET|LIMIT|STOP_LIMIT> --quantity <QTY> [--price <PRICE>] [--stop-price <STOP>]
```

### Examples

**Market Order — Buy 0.01 BTC**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

**Limit Order — Sell 0.01 BTC at $95,000**
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 95000
```

**Stop-Limit Order — Buy 0.1 ETH, trigger at $2380, limit at $2400**
```bash
python cli.py --symbol ETHUSDT --side BUY --type STOP_LIMIT --quantity 0.1 --price 2400 --stop-price 2380
```

**Passing credentials inline (instead of env vars)**
```bash
python cli.py --api-key YOUR_KEY --api-secret YOUR_SECRET --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

---

## Output

Each order prints a request summary and response details:

```
══════════════════════════════════════════════════
  ORDER REQUEST SUMMARY
══════════════════════════════════════════════════
  Symbol    : BTCUSDT
  Side      : BUY
  Type      : MARKET
  Quantity  : 0.01
══════════════════════════════════════════════════

✅  ORDER PLACED SUCCESSFULLY
──────────────────────────────────────────────────
  orderId        : 123456789
  symbol         : BTCUSDT
  side           : BUY
  type           : MARKET
  status         : FILLED
  origQty        : 0.01
  executedQty    : 0.01
  avgPrice       : 94823.50
──────────────────────────────────────────────────
```

---

## Logs

All API requests, responses, and errors are written to `logs/trading_YYYYMMDD.log`.

```
2025-03-14 10:22:01 | DEBUG    | client | REQUEST  POST /fapi/v1/order | params={...}
2025-03-14 10:22:02 | DEBUG    | client | RESPONSE 200 | body={...}
2025-03-14 10:22:02 | INFO     | orders | MARKET order placed | orderId=123456789 status=FILLED
```

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Missing required flags | Clear argparse error message |
| Invalid symbol / quantity / price | Validation error before any API call |
| API error (e.g. insufficient balance) | Prints error code and message, exits with code 1 |
| Network failure / timeout | Prints network error, exits with code 1 |
| Unexpected exception | Logs full traceback, prints friendly message |

---

## Assumptions

- Tested against Binance **USDT-M Futures Testnet** only (`https://testnet.binancefuture.com`)
- Default `timeInForce` for LIMIT orders is **GTC** (Good Till Cancelled); pass `--time-in-force IOC` or `FOK` to override
- STOP_LIMIT maps to Binance's `STOP` futures order type
- No external dependencies beyond `requests` — keeps the setup simple
