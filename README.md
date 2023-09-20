# tv-binance-bot
Python bot to use webhook signals from tradingview and create orders on binance futures. <br><br>
<strong>NOTE: </strong> <p>It will not work with hedge mode enabled.</p>

<strong>What you need to do:</strong><br>
You can change the following things in the settings.json file:
<li>whitelist (this is used as a password for your bot)</li>
<li>Binance API keys</li>
<li>Coin pairs to be whitelisted (it will only execute trades for those coins available in the whitelist)</li>
<li>Discord channel webhook URL</li><br>

<strong>TradingView Message JSON Format</strong><br>
{
"whitelist" : "tradingview-1m", (this should match the password called whitelist in settings.json file)<br>
"side" : "{{strategy.market_position}}", LONG or SHORT<br>
"symbol" : "{{ticker}}", (this would only work with perpetual pairs on tradingview, don't use it with spot pairs)<br>
"indicator" : "HullEMA", (any random name for your indicator)<br>
"comment": "{{strategy.order.comment}}" (if your strategy uses multiple trades as DCA then it will execute multiple trades in the same direction)<br>
}<br>

<strong>Features:</strong><br>
<li>Recieves signals from tradingview webhooks and executes trades based on them.</li>
<li>Sends notifications on discord server about executed trades.</li>
