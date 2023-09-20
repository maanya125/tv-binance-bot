import json,ccxt
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime


with open ('settings.json') as config_file:
    config = json.load(config_file)

comment = ''
trading_pairs = config['coins']
trade = config['trade_on_exchange']
key = config['api-key']
secret = config['api-secret']
leverage = config['leverage']
walletpercent = config['wallet_percent_per_order']
maxPosition = config['maxPercentPosition']
discord = config['discord']
discord_webhook  =  config['discord_channel_webhook']
ip = config['IP']
port = config['PORT']
exchang = config['exchange']
market = config['market']# spot, future, margin
exchange_class = getattr(ccxt, exchang)
exchange = exchange_class({'apiKey':key,
 'secret':secret,
 'timeout':30000,
 'enableRateLimit':True,
 'option':{'defaultMarket': market},
  'urls':{'api': {'public':'https://binance.com/fapi/v1',
          'private':'https://binance.com/fapi/v1'}}})
# exchange.set_sandbox_mode(True)
          
class signalhandler():

    def __init__(self):
        self._TIMEOUT = 5

    def send_discord(self):
        url = discord_webhook
        webhook = DiscordWebhook(url=url)
        embed = DiscordEmbed(title=(':boom: TradingView Indicators :boom:'), description='Signal received, Buy Position:', color=242424)
        embed.add_embed_field(name='Symbol:' , value=(str(self.Symbol)))
        embed.add_embed_field(name='Price:' , value=(str(round(self.last,4))))
        embed.add_embed_field(name='Coin Amount:' , value=(str(round(self.qty,3))))
        embed.add_embed_field(name='Indicator:' , value=(str(self.indicator.upper())))
        embed.add_embed_field(name='PositionSide:' , value=(str(self.s)))
        embed.set_timestamp()
        webhook.add_embed(embed)
        webhook.execute()


    def check_symbol(self):
        for asset in trading_pairs:
            if self.Symbol in asset:
                sh.get_account()


    def onsignal(self, data):
        jdata = json.loads(data.lower())
        self.Symbol = jdata['symbol'][:-4].upper()
        raw = self.Symbol[:-4] 
        self.coinSymbol = raw + '/USDT'
        self.buyside = "Long" if jdata['side'] == "buy" else "Short"
        self.indicator = jdata['indicator']
        self.comment = jdata['comment']

        sh.check_symbol()

            
    def get_account(self):
        ticker = exchange.fetch_ticker(self.coinSymbol)
        self.last = ticker['last']
        account = exchange.fapiPrivateGetAccount()
        balance = round(float(account['totalWalletBalance']), 2)
        qty1 = balance * leverage / 100  * walletpercent
        self.qty = qty1 / self.last
        print(self.Symbol,' TIME:', datetime.now().strftime('%H:%M:%S %m-%d'))
        print(self.Symbol,' Price: {}'.format(self.last))
        print(self.Symbol,' Amount  {}'.format(self.qty))
        print(self.Symbol,' Signal Side: {}'.format(self.buyside))
        print(self.Symbol,' Indicator: {}'.format(self.indicator))
        print(self.Symbol,' Balance: ', format(balance))
        self.maxPosition = balance / self.last * (maxPosition / 100 * leverage)
        sh.check_postions()    


    def check_postions(self):
        open_positions = exchange.fapiPrivateGetPositionRisk()

        for position in open_positions:
            sh.print_positions(position)
            if position['symbol'] == self.Symbol:
                if float(position['positionAmt']) > 0:
                    self.open_position = True
                    self.position = True
                    self.side = 'Long'
                    self.size = float(position['positionAmt'])
                    if(self.comment == 'Out Long'):
                        sh.close_previous('sell', self.size, self.Symbol)
                    elif(self.comment == 'short'):
                        sh.close_previous('sell', self.size, self.Symbol)
                        sh.create_position()
                if float(position['positionAmt']) < 0:
                    self.open_position = True
                    self.position = True
                    self.side = 'Short'
                    self.size = float(position['positionAmt'])
                    if(self.comment == 'Out Short'):
                        sh.close_previous('buy', self.size, self.Symbol)
                    elif(self.comment == 'long'):
                        sh.close_previous('buy', self.size, self.Symbol)
                        sh.create_position()
                if float(position['positionAmt']) == 0:
                    self.open_position = False
                    self.side = None
                    self.size = 0
                    sh.create_position()

    def print_positions(self, position):
        if position['symbol'] == self.Symbol:
            try:
                print('------------Opened Position----------------')
                print('Symbol:', position['symbol'])
                print('Position Side:', position['positionSide'])
                print('Position Amount:', position['positionAmt'])
                print('Entry Price:', position['entryPrice'])
                print('Unrealized PNL:', position['unRealizedProfit'])
                print('Leverage:', position['leverage'])
                print('----------------------------')
            except KeyError:
                print("Missing key in position data")


    def close_previous(self, side, size, symbol):
        params = {
            'reduceOnly': True,  # On exit orders
        }

        order = exchange.create_order(
            symbol=symbol,
            type='MARKET',
            side=side,
            amount=abs(size),
            params=params
        )
        if(order):
            self.size = 0
        # print the order response
        print(order)

    def create_position(self):
        if abs(self.size) <= self.maxPosition:
            if self.buyside == 'Long':
                if self.side == None or self.side == 'Short':
                    print("executing long")
                    if trade:
                        sh.set_leverage()
                        exchange.create_market_buy_order(self.coinSymbol, self.qty)
                    print('##############################################')
                    print(self.Symbol,': BUY LONG!')
                    print('##############################################')
                    self.orderside = "Long"
                    if discord:
                        self.s = ':chart_with_downwards_trend:LONG:chart_with_downwards_trend:'
                        sh.send_discord()
            else:
                if self.buyside == 'Short':
                    print('Short')
                    if self.side == None or self.side == 'Long':
                        print("executing short")
                        if trade:
                            sh.set_leverage()
                            exchange.create_market_sell_order(self.coinSymbol, self.qty )
                        print('##############################################')
                        print(self.coinSymbol,': Short BUY!')
                        print('##############################################')
                        self.orderside = "Short"
                        if discord:
                            self.s = ':chart_with_upwards_trend:Short:chart_with_upwards_trend:'
                            sh.send_discord()
        else:
            if abs(self.size) >= self.maxPosition:
                print(self.coinSymbol,'MAX Invest reached !!!')

    def set_leverage(self):
        params = {'symbol':self.Symbol,
         'reduceOnly':False,
         'closePosition': False,
         'leverage':leverage}
        exchange.fapiPrivatePostLeverage(params=params)

sh = signalhandler()
