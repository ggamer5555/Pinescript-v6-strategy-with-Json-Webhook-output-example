# Pinescript-v6-strategy-with-Json-Webhook-output-example
This PineScript V6 program places dollar cost averaging trades for 2 different strategies and uses arrays of arrays to store data. The strategies compute a signal with TP and SL with a passphrase for the receiving server to accept for security, then send the Json format Webhook with alert feature for the strategy.

# LIVE ALERTS PYTH MT5 — TradingView Webhook Strategy

A TradingView Pine Script strategy designed to generate live JSON alerts for an external Python / MT5 execution bridge.

The script is written in Pine Script v6 and runs as a TradingView `strategy()`. It calculates multi-timeframe trend, volatility, imbalance, Bollinger Band Width, and DCA trade states. TradingView is then used to send the current trade state to a webhook as JSON.

> Important: Pine Script cannot directly place trades in MetaTrader 5.  
> This script creates TradingView strategy orders for backtesting/visual tracking and sends webhook alerts. A separate webhook receiver, Python bridge, or MT5 EA must receive the alert JSON and place the real MT5 trades.

---

## Strategy Summary

This strategy is a hybrid mean-reversion / DCA system that uses:

- Dynamic higher-timeframe EMA trend filtering
- Bollinger Band Width volatility regimes
- Normal imbalance entries
- BBW low-volatility imbalance entries
- DCA safety orders
- Take-profit and stop-loss levels
- JSON webhook alerts for external execution
- Separate state fields for normal, BBW, and placeholder OI trade groups

The TradingView strategy name is:

```pine
strategy('LIVE ALERTS PYTH MT5', overlay = true)
```

The strategy is designed to watch price action on TradingView, decide whether the system should be long, short, or flat, and then publish those states through a webhook message.

---

## High-Level Flow

```text
TradingView chart
      |
      v
Pine Script strategy calculates:
- Trend
- Volatility regime
- Entry conditions
- DCA state
- TP / SL levels
      |
      v
Pine Script builds JSON alert payload
      |
      v
TradingView alert sends JSON to webhook URL
      |
      v
Python / MT5 bridge validates passphrase
      |
      v
Bridge opens, updates, or closes MT5 trades
```

---

## Main Strategy Components

## 1. Dynamic Volatility Regime

The script calculates a higher-timeframe Bollinger Band Width value.

The default BBW timeframe is:

```pine
bbw_timeframe = "240"
```

That means the strategy uses a 4-hour volatility regime while it can run on a lower chart timeframe.

The script calculates Bollinger Band Width and then sorts the market into different active levels:

```text
Level 1: very low BBW
Level 2: low BBW
Level 3: moderate BBW
Level 4: rising BBW
Level 5+: higher volatility
```

Each volatility level can change the active settings, including:

- Minimum price imbalance required
- Entry limit offset
- Stop-loss percentage
- BBW entry offset
- Dynamic EMA parameters
- Whether a trade level is enabled

This allows the same strategy to behave differently depending on the volatility environment.

---

## 2. Higher-Timeframe Dynamic EMA

The strategy calculates a dynamic EMA and requests it from another timeframe:

```pine
ema_Period = "15"
```

The EMA trend is classified as:

```text
ht_ema_trend = 1   bullish / rising EMA
ht_ema_trend = -1  bearish / falling EMA
ht_ema_trend = 0   neutral / unchanged
```

The EMA trend is used as a major trade filter.

Normal long DCA trades require bullish EMA trend.

Normal short DCA trades require bearish EMA trend.

If the EMA trend flips against an open normal DCA position, the script closes that position in the TradingView strategy logic.

---

## 3. Normal Imbalance Strategy

The normal imbalance part of the strategy looks for price extending away from recent highs or lows, then prepares a DCA entry.

### Normal Long Setup

A normal long setup is prepared when price breaks below recent lows while the higher-timeframe EMA trend remains bullish.

The logic is roughly:

```text
1. Price breaks below recent low range.
2. Move is large enough compared with the configured minimum imbalance.
3. Normal longs are enabled.
4. Higher-timeframe EMA trend is bullish.
5. Consolidation filter is below the max line.
6. No existing normal small trade is active.
7. A long DCA trigger is stored.
```

When this setup is active, the script stores:

```text
limitEntry_short
L_SLline
limitClose1
normOrder_active
```

The actual normal long DCA position is opened later if price reaches the DCA trigger level.

### Normal Short Setup

A normal short setup is prepared when price breaks above recent highs while the higher-timeframe EMA trend remains bearish.

The logic is roughly:

```text
1. Price breaks above recent high range.
2. Move is large enough compared with the configured minimum imbalance.
3. Normal shorts are enabled.
4. Higher-timeframe EMA trend is bearish.
5. Consolidation filter is below the max line.
6. No existing normal small trade is active.
7. A short DCA trigger is stored.
```

When this setup is active, the script stores:

```text
limitEntry_long
S_SLline
limitClose1
normOrder_active
```

---

## 4. BBW Imbalance Strategy

The BBW strategy is a low-volatility imbalance strategy.

It becomes active when the current Bollinger Band Width is below the selected threshold:

```pine
BBW_active = 1
```

The BBW logic is designed to trade low-volatility imbalance conditions and uses its own entry arrays, stop lines, close lines, and DCA system.

BBW trade direction is controlled by:

```pine
BBW_SHORT_ALLOWED
BBW_LONG_ALLOWED
```

The BBW strategy also uses session filters. The script references Friday, Saturday, and Sunday time windows and only allows certain BBW logic when those time filters are active.

### BBW Long Setup

A BBW long setup is prepared when:

```text
1. BBW is active.
2. BBW longs are allowed.
3. The session filter allows the setup.
4. Price breaks below the previous low.
5. EMA/color condition confirms the setup.
6. No BBW small trade is currently active.
7. A BBW long DCA trigger is stored.
```

### BBW Short Setup

A BBW short setup is prepared when:

```text
1. BBW is active.
2. BBW shorts are allowed.
3. The session filter allows the setup.
4. Price breaks above the previous high.
5. EMA/color condition confirms the setup.
6. No BBW small trade is currently active.
7. A BBW short DCA trigger is stored.
```

---

## 5. DCA Trade Engine

The active trade placement in TradingView is done with `strategy.entry()` and `strategy.close()`.

The script has four main DCA engines:

| Engine | Direction | TradingView Entry ID | Purpose |
|---|---:|---|---|
| Normal Long DCA | Long | `LSODCA` | Normal imbalance long |
| Normal Short DCA | Short | `SSODCA` | Normal imbalance short |
| BBW Long DCA | Long | `LSOBBW` | BBW imbalance long |
| BBW Short DCA | Short | `SSOBBW` | BBW imbalance short |

The code also includes an OI alert slot using `LSOOI` / `SSOOI`, but the provided script does not actively create those entries. The OI fields are included in the webhook payload as a placeholder or extension point.

---

# How Trades Are Placed

## TradingView Backtest / Strategy Trades

Inside TradingView, trades are placed by Pine Script using `strategy.entry()`.

Example normal long DCA entry:

```pine
strategy.entry("LSODCA", strategy.long, qty = (strategy.equity * base_order / 100) / close)
```

Example normal short DCA entry:

```pine
strategy.entry("SSODCA", strategy.short, qty = (strategy.equity * base_S_order / 100) / close)
```

Example BBW long DCA entry:

```pine
strategy.entry("LSOBBW", strategy.long, qty = (strategy.equity * base_order_L_BBW / 100) / close)
```

Example BBW short DCA entry:

```pine
strategy.entry("SSOBBW", strategy.short, qty = (strategy.equity * base_S_order_BBW / 100) / close)
```

These entries are TradingView strategy orders. They are used for backtesting, plotting, and generating state.

---

## DCA Safety Orders

After the first DCA position opens, the script can add more entries using safety orders.

For long DCA trades, the script averages down when price moves below the calculated threshold.

For short DCA trades, the script averages up when price moves above the calculated threshold.

Safety order settings include:

```pine
price_deviation
safe_order
safe_order_volume_scale
safe_order_step_scale
max_safe_order
```

Normal DCA defaults include:

```text
Normal base order: 1.4% of equity
Normal safe order: base_order * 2
Normal max safety orders: 4
```

BBW DCA defaults include:

```text
BBW base order: 30% of equity
BBW safe order: base_order_L_BBW
BBW max safety orders: 2
```

The position size formula is based on strategy equity and current close price:

```text
quantity = (strategy.equity * order_percent / 100) / close
```

---

## Take Profit and Stop Loss

The strategy uses stored close levels and stop lines.

Normal long:

```text
TP: limitClose1[2]
SL: L_SLline[0]
```

Normal short:

```text
TP: limitClose1[0]
SL: S_SLline[0]
```

BBW long:

```text
TP: BBW_LimitClose[2], adjusted by current BBW safety order count
SL: BBW_L_SLline[0]
```

BBW short:

```text
TP: BBW_LimitClose[0], adjusted by current BBW safety order count
SL: BBW_S_SLline[0]
```

The script closes TradingView strategy positions with `strategy.close()` when TP, SL, session, or trend-flip conditions occur.

---

## External MT5 Trade Placement

For live MetaTrader 5 execution, the Pine Script does not place the trades directly.

Instead:

1. Pine Script calculates the current desired trade state.
2. Pine Script sends that state as a JSON alert.
3. TradingView posts the alert to a webhook URL.
4. A Python server, Flask/FastAPI app, or MT5 bridge receives the JSON.
5. The receiver validates the `passphrase`.
6. The receiver reads the side, TP, SL, and EMA fields.
7. The receiver opens, updates, or closes MT5 trades.

A typical receiver should compare the latest alert state with existing MT5 positions.

For example:

```text
side1 = 1   -> normal DCA should be long
side1 = -1  -> normal DCA should be short
side1 = 0   -> no normal DCA trade should be open

side2 = 1   -> BBW DCA should be long
side2 = -1  -> BBW DCA should be short
side2 = 0   -> no BBW DCA trade should be open
```

---

# How the Webhook Works

At the end of the script, the Pine code builds a JSON string.

The payload includes:

```json
{
  "passphrase": "example",
  "side1": "0",
  "side2": "0",
  "side3": "0",
  "TP1": "0",
  "TP2": "0",
  "TP3": "0",
  "SL1": "0",
  "SL2": "0",
  "SL3": "0",
  "EMA": "0"
}
```

The alert is sent with:

```pine
alert(alertstring, alert.freq_all)
```

This means TradingView can send the alert whenever the script executes and the alert call fires.

---

## Webhook Field Meanings

| Field | Meaning |
|---|---|
| `passphrase` | Shared secret used by the webhook receiver to reject unauthorized alerts. |
| `side1` | Normal DCA direction. `1` = long, `-1` = short, `0` = flat. |
| `side2` | BBW DCA direction. `1` = long, `-1` = short, `0` = flat. |
| `side3` | OI strategy slot. Included as a placeholder/extension field. |
| `TP1` | Take-profit level for normal DCA. |
| `TP2` | Take-profit level for BBW DCA. |
| `TP3` | Take-profit level for OI slot. |
| `SL1` | Stop-loss level for normal DCA. |
| `SL2` | Stop-loss level for BBW DCA. |
| `SL3` | Stop-loss level for OI slot. |
| `EMA` | Higher-timeframe EMA trend. `1` = bullish, `-1` = bearish. |

---

## Webhook Example: Normal Long Active

```json
{
  "passphrase": "example",
  "side1": "1",
  "side2": "0",
  "side3": "0",
  "TP1": "68450.25",
  "TP2": "0",
  "TP3": "0",
  "SL1": "66100.00",
  "SL2": "0",
  "SL3": "0",
  "EMA": "1"
}
```

Meaning:

```text
Normal DCA system wants to be long.
Normal TP is 68450.25.
Normal SL is 66100.00.
BBW and OI systems are flat.
EMA trend is bullish.
```

---

## Webhook Example: BBW Short Active

```json
{
  "passphrase": "example",
  "side1": "0",
  "side2": "-1",
  "side3": "0",
  "TP1": "0",
  "TP2": "67250.00",
  "TP3": "0",
  "SL1": "0",
  "SL2": "70100.00",
  "SL3": "0",
  "EMA": "-1"
}
```

Meaning:

```text
BBW DCA system wants to be short.
BBW TP is 67250.00.
BBW SL is 70100.00.
Normal and OI systems are flat.
EMA trend is bearish.
```

---

# Suggested Webhook Receiver Logic

A Python / MT5 receiver can use logic like this:

```python
payload = request.json

if payload["passphrase"] != EXPECTED_PASSPHRASE:
    reject_alert()

normal_side = int(float(payload["side1"]))
bbw_side = int(float(payload["side2"]))

normal_tp = float(payload["TP1"])
normal_sl = float(payload["SL1"])

bbw_tp = float(payload["TP2"])
bbw_sl = float(payload["SL2"])

if normal_side == 1:
    open_or_hold_long(strategy="normal", tp=normal_tp, sl=normal_sl)
elif normal_side == -1:
    open_or_hold_short(strategy="normal", tp=normal_tp, sl=normal_sl)
else:
    close_or_hold_flat(strategy="normal")

if bbw_side == 1:
    open_or_hold_long(strategy="bbw", tp=bbw_tp, sl=bbw_sl)
elif bbw_side == -1:
    open_or_hold_short(strategy="bbw", tp=bbw_tp, sl=bbw_sl)
else:
    close_or_hold_flat(strategy="bbw")
```

The receiver should avoid opening duplicate positions by checking existing MT5 trades before sending new orders.

---

# TradingView Alert Setup

To use the webhook output:

1. Add the strategy to a TradingView chart.
2. Click **Alert**.
3. Select the strategy as the alert condition.
4. Use an alert condition that captures `alert()` function calls.
5. Enable **Webhook URL**.
6. Paste your webhook endpoint URL.
7. Use the script-generated alert message.
8. Make sure your receiver checks the `passphrase`.

The alert payload is generated inside the script, so the external receiver should parse the JSON body sent by TradingView.

---

# Important Implementation Notes

## The Pine Script Emits State, Not Broker Orders

The script sends the full current state on each alert.

Your MT5 bridge should treat the alert as an instruction/state update, not blindly open a new trade every time.

For example, if `side1` remains `1` across many alerts, the receiver should not open a new normal long position on every alert. It should detect that the normal long is already open and hold/update it.

---

## Use Separate Magic Numbers or Comments

For MT5 execution, use different identifiers for each strategy bucket:

```text
normal DCA  -> side1
BBW DCA     -> side2
OI slot     -> side3
```

Recommended MT5 comments:

```text
TV_NORMAL_DCA
TV_BBW_DCA
TV_OI_SLOT
```

This helps the execution bridge update and close the correct trades.

---

## Recommended Receiver Safety Checks

A production webhook receiver should check:

- Passphrase validity
- Symbol allowlist
- Payload JSON validity
- Numeric conversion safety
- Maximum lot size
- Minimum lot size
- Broker trading hours
- Spread limit
- Duplicate-position protection
- Maximum open trades
- Maximum daily loss
- Maximum account drawdown
- TP/SL sanity checks
- Alert timestamp freshness

---

# Strategy Settings Overview

## Main Order Inputs

| Input | Meaning |
|---|---|
| `base_order` | Normal DCA base order percentage of equity. |
| `base_order_L_BBW` | BBW DCA base order percentage of equity. |
| `normalSHORTS_allowed` | Enables/disables normal short setups. |
| `normalLONGS_allowed` | Enables/disables normal long setups. |
| `BBW_SHORT_ALLOWED` | Enables/disables BBW short setups. |
| `BBW_LONG_ALLOWED` | Enables/disables BBW long setups. |
| `MED_trades_allowed` | Medium trade toggle; much of the medium logic appears inactive/commented. |

---

## Volatility / BBW Inputs

| Input | Meaning |
|---|---|
| `bbw_timeframe` | Higher timeframe used for BBW regime. Default is 4h. |
| `length_bbw_ema` | BBW smoothing input. |
| `length_bbw` | EMA length used to smooth BBW. |
| `bbw_input_change` | Threshold used to activate BBW logic. |
| `BBW_stop_loss` | Stop-loss percent used by BBW setups. |
| `BBW_entryLimit_offset` | Entry offset for BBW DCA triggers. |

---

## Normal DCA Inputs

| Input | Meaning |
|---|---|
| `price_deviation` | Distance before opening long safety orders. |
| `safe_order` | Normal long safety order size. |
| `safe_order_volume_scale` | Multiplier for normal long safety order size. |
| `safe_order_step_scale` | Multiplier for normal long safety order spacing. |
| `max_safe_order` | Maximum normal long safety orders. |
| `price_S_deviation` | Distance before opening short safety orders. |
| `safe_S_order` | Normal short safety order size. |
| `safe_S_order_volume_scale` | Multiplier for normal short safety order size. |
| `safe_S_order_step_scale` | Multiplier for normal short safety order spacing. |
| `max_S_safe_order` | Maximum normal short safety orders. |

---

## BBW DCA Inputs

| Input | Meaning |
|---|---|
| `price_deviation_L_BBW` | Distance before opening BBW long safety orders. |
| `safe_order_L_BBW` | BBW long safety order size. |
| `safe_order_volume_scale_L_BBW` | Multiplier for BBW long safety order size. |
| `safe_order_step_scale_L_BBW` | Multiplier for BBW long safety order spacing. |
| `max_safe_order_L_BBW` | Maximum BBW long safety orders. |
| `price_S_deviation_BBW` | Distance before opening BBW short safety orders. |
| `safe_S_order_BBW` | BBW short safety order size. |
| `safe_S_order_volume_scale_BBW` | Multiplier for BBW short safety order size. |
| `safe_S_order_step_scale_BBW` | Multiplier for BBW short safety order spacing. |
| `max_S_safe_order_BBW` | Maximum BBW short safety orders. |

---

# Risk Warning

This strategy uses DCA and safety orders. DCA can increase exposure as price moves against the position.

Before live use:

- Backtest the exact symbol and timeframe.
- Forward-test with paper trading or demo execution.
- Confirm TradingView alerts match MT5 execution.
- Use hard account-level risk limits.
- Confirm the webhook receiver does not duplicate trades.
- Confirm TP and SL values are mapped correctly.
- Start with very small size.

---

# Repository Structure

Suggested GitHub layout:

```text
tradingview-live-alerts-pyth-mt5/
│
├── README.md
├── pine/
│   └── live_alerts_pyth_mt5.pine
│
├── webhook/
│   └── receiver_example.py
│
├── mt5/
│   └── mt5_execution_bridge.py
│
└── docs/
    └── webhook-payload.md
```

---

# Disclaimer

This project is for educational and research purposes. It is not financial advice. Automated trading carries substantial risk, especially when using DCA, leverage, futures, crypto, or live broker execution.

Use at your own risk.
