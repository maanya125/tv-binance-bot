# tv-binance-bot

**Description:** Python bot for creating orders on Binance Futures using webhook signals from TradingView.

**Note:** This bot does not work with hedge mode enabled.

## Setup

Before using this bot, make sure to configure the following settings in the `settings.json` file:

- **Whitelist:** This is used as a password for your bot.
- **Binance API keys**
- **Coin pairs to be whitelisted:** The bot will only execute trades for coins available in the whitelist.
- **Discord channel webhook URL**

## TradingView Message JSON Format

The signals from TradingView should follow this JSON format:

```json
{
    "whitelist" : "tradingview-1m", // This should match the password in the `settings.json` whitelist.
    "side" : "{{strategy.market_position}}", // Either LONG or SHORT.
    "symbol" : "{{ticker}}", // This only works with perpetual pairs on TradingView, do not use it with spot pairs.
    "indicator" : "HullEMA", // Choose any random name for your indicator.
    "comment": "{{strategy.order.comment}}" // If your strategy involves multiple trades as DCA, it will execute multiple trades in the same direction.
}
