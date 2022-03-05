from collections import defaultdict

class TestAccount: 

    def __init__(self, balance=5000):
        """
        Holder for account variables. Initializes with an empty porfolio 
        and $5000 available cash to spend, unless a custom balance is provided.  
        """
        self.balance = balance
        self.open_positions = [] # list of dicts holding open trading positions by type
        self.trade_history = [] # container for past trades


    def trade(self, type, symbol, price, quantity, stoploss, profittarget, latestdate): 
        """
        Args: 
            type (str): buy or short
            symbol (str): ticker to trade (TODO: This will work for now, since all quote currency is USD)
            price (float): buy price - calculated as the midpoint of the latest candle's open and close prices
            quantity (float): qty to buy - calculated based on the desired trading amount in strategy.py and the price of the symbol
            stoploss (float): price below which to sell on a bullish trade or buy / close for a short position
            profittarget (float): price above which to sell to take profit on a bullish trade, or the reverse for a short position
            latestdate (int): datetime of the execution of the trading event - today for live trading, historical dates for backtesting

        Returns:
            None: updates TestAccount attributes
        """
        
        ''' TEMP: removing affordability check and allowing balance to go below zero
        balance_required = price * qty
        if balance_required > self.balance: 
            print('Buy error: Not enough cash to execute trade for {0} {1} at {2} (total \
                balance required: {3}). Porfolio only has {4} available cash to spend.'.format(qty, 
                symbol, price, balance_required, self.balance))
        else: # execute trade
            self.portfolio[symbol] += qty
            self.balance -= balance_required
            self.trade_history.append([time, 'buy', symbol, price, qty])
        '''

        # Execute trade, decrement balance, and add to open_positions based on trade type

        # Buy scenario
        if type == "buy": 
            # TODO: API call placeholder
            self.balance -= price * quantity
            self.open_positions.append({"time": latestdate,
                                        "symbol": symbol,
                                        "price": price,
                                        "quantity": quantity,
                                        "stoploss": stoploss,
                                        "profittarget": profittarget,
                                        "status": True})

        # Short scenario

    def close(self, symbol, price): 
        """
        Args: 
            symbol (str): security to execute against
            price (float): midpoint of the open / close price of the latest candle

        Returns:
            None: updates TestAccount attributes
        """
        # Iterate through all open positions for the relevant symbol
        for position in self.open_positions:
            if position["symbol"] == symbol:

                # Check if the price breaks the position's profit target and if the position is still open
                if price >= position["profittarget"] and position["status"] == True:

                    # If so, credit the balance by the price multiplied by the position's quantity and set the status to False
                    self.balance += price * position["quantity"]
                    position["status"] = False
                
                # Check if the price breaks the position's stop-loss and if the position is still open
                elif price < position["stoploss"] and position["status"] == True:

                    # If so, credit the balance by the price multiplied by the position's quantity and set the status to False
                    self.balance += price * position["quantity"]
                    position["status"] = False
    
    def get_balance(self):
        return self.balance

    def get_open_positions(self):
        return self.open_positions

    def get_trade_history(self):
        return self.trade_history

class Account: 

    def __init__(self, username, password):
        """
        Holder for account variables. Initializes with user credentials to authenticate
        with Coinbase. 
        """
        # TODO: Authenticate with Coinbase
        pass


    def buy(self, symbol, price, qty, time=None): 
        """
        Args: 
            symbol (str): ticker to trade (TODO: This will work for now, since all quote currency is USD)
            price (float): buy price
            qty (float): qty to buy
            time (int): timestamp of trade

        Returns:
            PKC: returns / stores trade confirmation data from trading API?
        """
        # TODO: Get from Coinbase API
        pass
    

    def sell(self, symbol, price, qty, time=None): 
        """
        Args: 
            symbol (str): ticker to trade (TODO: This will work for now, since all quote currency is USD)
            price (float): sell price
            qty (float): qty to sell
            time (int): timestamp of trade

        Returns:
            None
        """
        # TODO: Get from Coinbase API
        pass
    
    def get_balance(self):
        # TODO: Get from Coinbase API
        pass

    def get_portfolio(self):
        # TODO: Get from Coinbase API
        pass

    def get_trade_history(self):
        # TODO: Get from Coinbase API
        pass
    