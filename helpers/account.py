from collections import defaultdict

class TestAccount: 

    def __init__(self, balance=5000):
        """
        Holder for account variables. Initializes with an empty porfolio 
        and $5000 available cash to spend, unless a custom balance is provided.  
        """
        self.balance = balance
        self.portfolio = defaultdict(float)
        self.trade_history = [] # container for past trades


    def buy(self, symbol, price, qty, time=None): 
        """
        Args: 
            symbol (str): ticker to trade (TODO: This will work for now, since all quote currency is USD)
            price (float): buy price
            qty (float): qty to buy
            time (int): timestamp of trade

        Returns:
            None: updates TestAccount attributes
        """
        balance_required = price * qty
        if balance_required > self.balance: 
            print('Buy error: Not enough cash to execute trade for {0} {1} at {2} (total \
                balance required: {3}). Porfolio only has {4} available cash to spend.'.format(qty, 
                symbol, price, balance_required, self.balance))
        else: # execute trade
            self.portfolio[symbol] += qty
            self.balance -= balance_required
            self.trade_history.append([time, 'buy', symbol, price, qty])
    

    def sell(self, symbol, price, qty, time=None): 
        """
        Args: 
            symbol (str): ticker to trade (TODO: This will work for now, since all quote currency is USD)
            price (float): sell price
            qty (float): qty to sell
            time (int): timestamp of trade

        Returns:
            None: updates TestAccount attributes
        """
        if self.portfolio[symbol] < qty: 
            print('Sell error: Not enough {0} to execute trade for {1} {2} at {3} (portfolio \
                contains {4} {5}).'.format(symbol, qty, symbol, price, self.portfolio[symbol], 
                symbol))
        else: # execute trade
            self.portfolio[symbol] -= qty
            self.balance += qty * price
            self.trade_history.append([time, 'sell', symbol, price, qty])
    
    def get_balance(self):
        return self.balance

    def get_portfolio(self):
        return self.portfolio

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
            None
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
    