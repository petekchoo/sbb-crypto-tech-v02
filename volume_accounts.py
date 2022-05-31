from collections import defaultdict
from datetime import datetime, timedelta

class TestAccount: 

    def __init__(self, balance, profit, stoploss):
        """
        Holder for account variables. Initializes with an empty porfolio 
        and $5000 available cash to spend, unless a custom balance is provided.  
        """
        self.balance = balance
        self.trade_value = balance / 100 # Starting trade values are 1% of account value
        self.open_positions = [] # List of dicts holding open trading positions by type
        self.max_drawdown = balance # Lowest value reached either during opening or updating a position
        self.portfolio_value = 0
        self.profit_multiple = profit
        self.stop_loss = stoploss

    def open_position(self, type, symbol, price, quantity, stoploss, profittarget, latestdate): 
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
        # TODO: API call placeholder
        
        # Check if buy or short - if buy, decrement balance.
        # If taking a short position, do not decrement balance (liabilities will be tracked via update, final positions via close)
        if type == "buy":
            self.balance -= price * quantity

        # If the new balance is lower than the current maximum drawdown, update drawdown to current balance
        # NOTE: for backtesting purposes, balances will be allowed to trade below zero...
        #   for live testing, a balance check with a deposit, credit, or trade rejection behavior
        if self.balance < self.max_drawdown:
            self.max_drawdown = self.balance

        # Add the newest position to the open positions of the TestAccount object.
        # Note that the effective date of the position is technically the following day, as are any updates,
        # since trade decisions are made after the close of the 'current day' in the trading strategy
        self.open_positions.append({"time": latestdate,
                                    "symbol": symbol,
                                    "type": type,
                                    "init_price": price,
                                    "current_price": price,
                                    "close_price": None,
                                    "close_time": None,
                                    "quantity": quantity,
                                    "stoploss": stoploss,
                                    "profittarget": profittarget,
                                    "status": True})

    def update_positions(self, symbol, price, latestdate):
        '''
        Called from strategy to update the value of positions for a given symboland a latest midpoint price
        For buy positions, no impact to balance
        For short positions, account balance is increased or decreased since liability changes based on latest price until position close
        Args:
            symbol (str): security to update based on latest price
            price (float): the midpoint of the open / close price of the latest candle
        '''
        # Iterate through all open positions for the relevant symbol
        for position in self.open_positions:
            if position["symbol"] == symbol and position["time"] < latestdate and bool(position["status"]) == True:

                # If position is a buy, simply update current_price
                if position["type"] == "buy":
                    position["current_price"] = price
                
                # If position is a short, determine the new account value relative to the current price:
                elif position["type"] == "short":

                    # If the previous current price is greater than the new price, credit the balance the difference * qty
                    # and update current price
                    if float(position["current_price"]) >= price:

                        self.balance += (float(position["current_price"]) - price) * float(position["quantity"])
                        position["current_price"] = price
                    
                    # If the previous current price is less than the new price, decrement the balance difference * qty
                    # and update current price
                    elif float(position["current_price"]) < price:

                        self.balance -= (price - float(position["current_price"])) * float(position["quantity"])
                        position["current_price"] = price
                        
                        # If a new max drawdown has occurred, update that with the current balance
                        if self.balance < self.max_drawdown:
                            self.max_drawdown = self.balance
    
    def close_positions(self, symbol, price, latestdate): 
        """
        Args: 
            symbol (str): security to execute against
            price (float): midpoint of the open / close price of the latest candle

        Returns:
            None: updates TestAccount attributes
        """
        # Iterate through all open positions for the relevant symbol
        for position in self.open_positions:
            
            # Check for positions that match the given symbol and were opened prior to the current effective date and are still open
            if position["symbol"] == symbol and position["time"] < latestdate and bool(position["status"]) == True:
                
                # Branch for buy scenarios
                if position["type"] == "buy":

                    # Check if the price breaks the position's profit target and if the position is still open
                    if price >= float(position["profittarget"]):

                        # If so, credit the balance by the price multiplied by the position's quantity,
                        # record the closing price and date of the position, and set the status to False
                        self.balance += price * float(position["quantity"])
                        position["close_price"] = price
                        position["close_time"] = latestdate
                        position["status"] = False
                    
                    # Check if the price breaks the position's stop-loss and if the position is still open
                    elif price < float(position["stoploss"]):

                        # If so, credit the balance by the price multiplied by the position's quantity,
                        # record the closing price of the position, and set the status to False
                        self.balance += price * float(position["quantity"])
                        position["close_price"] = price
                        position["close_time"] = latestdate
                        position["status"] = False
                
                # Branch for short scenarios
                elif position["type"] == "short":

                    # Check if the price breaks the position's profit target and if the position is still open
                    if price <= float(position["profittarget"]):

                        # If so, liability would have already been posted during the update function, 
                        # set close price to current price and close the position
                        position["close_price"] = price
                        position["close_time"] = latestdate
                        position["status"] = False
                    
                    # Check if the price breaks the position's stop-loss and if the position is still open
                    elif price > float(position["stoploss"]):

                        # If so, liability would have already been posted during the update function, 
                        # set close price to current price and close the position 
                        position["close_price"] = price
                        position["close_time"] = latestdate
                        position["status"] = False
    
    def get_balance(self):
        return self.balance

    def get_open_positions(self):
        return self.open_positions

    def get_portfolio_value(self):
        
        # Initialize open positions to zero to start
        self.portfolio_value = 0

        # Iterate through all open (True) buy positions, multiply current price (if available) * qty
        for position in self.open_positions:

            if position["type"] == "buy" and bool(position["status"]) == True:
                if position["current_value"] != None:
                    self.portfolio_value += float(position["current_value"]) * float(position["quantity"])
                
                elif position["current_value"] == None:
                    self.portfolio_value += float(position["init_value"]) * float(position["quantity"])
        
        return self.portfolio_value

'''
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
'''