from plotter import Plotter
from data_manager import DataManager
import pandas as pd

class Backtest():
    """
    Manages the backtesting process, including applying strategies to assets, computing PnL, and aggregating results.
    Attributes:
        config (Config): Configuration parameters.
        assets (list of Asset): List of Asset instances to be backtested.
        strategies (list of Strategy): List of Strategy instances to be applied.
        results (pd.DataFrame): DataFrame to store summary results of the backtest.
        trade_logs (list of dict): List to store detailed trade logs.
    """
# ______________________________________________________________________________________________
    def __init__(self, config, assets, strategies):
        """
        Initializes the Backtester instance.
        Parameters:
            config (Config): Configuration parameters.
            assets (list of Asset): List of Asset instances to be backtested.
            strategies (list of Strategy): List of Strategy instances to be applied.
        """
        self.config = config
        self.assets = assets
        self.strategies = strategies
        self.results = pd.DataFrame(columns = [
            'Asset', 'Strategy', 'Strategy Params', 'Total PnL', 'Win Rate'
        ])
        self.trade_logs = []
# ______________________________________________________________________________________________
    def run_backtest(self, start, end, year, window = 14):
        """
        Executes the backtesting process for a given time period.
        Parameters:
            start (str): Start date in 'YYYY-MM-DD' format.
            end (str): End date in 'YYYY-MM-DD' format.
            year (int): Year of the backtest.
            window (int, optional): RSI window size (default is 14).
        """

        for asset in self.assets:
            print(f"Processing Asset: {asset.ticker} for Year: {year}")
            asset.fetch_data(start, end)
            if asset.data.empty:
                continue  # Skip assets with no data
            
            for strategy in self.strategies:
                # Assign the current asset to the strategy
                strategy.asset = asset
                strategy.generate_signals()
                pnl, win_rate, trades = self.compute_pnl(asset, strategy)
                
                # Record results
                self.results = self.results.append({
                    'Asset': asset.ticker,
                    'Strategy': type(strategy).__name__,
                    'Strategy Params': strategy.params,
                    'Total PnL': pnl,
                    'Win Rate': win_rate
                }, ignore_index = True)
                
                # Append trade logs
                self.trade_logs.extend(trades)
                
                # Plotting and Saving
                plotter = Plotter(
                    config = self.config, 
                    asset = asset, 
                    strategy = strategy, 
                    trades = trades, 
                    pnl = pnl, 
                    year = year
                )
                plotter.plot_and_save()
        
        # After all assets and strategies are processed, save the results
        data_manager = DataManager(config=self.config)
        data_manager.save_results(self.results, self.trade_logs, year)
# ______________________________________________________________________________________________    
    def compute_pnl(self, asset, strategy):
        """
        Computes the Profit and Loss (PnL) and Win Rate based on generated signals.
        Parameters:
            asset (Asset): The asset being analyzed.
            strategy (Strategy): The strategy applied.
        Returns:
            tuple:
                total_pnl (float): Total PnL for the strategy.
                win_rate (float): Percentage of winning trades.
                trade_logs (list of dict): Detailed trade logs.
        """
        signals = strategy.signals
        data = asset.data.copy()
        data = data.join(signals)
        
        # Identify entry points
        entry_points = data[(data['Long Trigger'] == 1) | (data['Short Trigger'] == -1)].index
        
        total_pnl = 0
        win_count = 0
        trade_logs = []
        
        for entry_point in entry_points:
            trigger_long = data.at[entry_point, 'Long Trigger']
            trigger_short = data.at[entry_point, 'Short Trigger']
            
            if trigger_long == 1:
                # Find next short trigger as exit
                exit_points = data[(data['Short Trigger'] == -1) & (data.index > entry_point)]
                if not exit_points.empty:
                    exit_point = exit_points.index[0]
                else:
                    exit_point = data.index[-1]  # Exit at last available point
                
                entry_price = data.at[entry_point, 'Adj Close']
                exit_price = data.at[exit_point, 'Adj Close']
                pnl = (exit_price - entry_price) / entry_price * 100.0  # Percentage PnL
            
            elif trigger_short == -1:
                # Find next long trigger as exit
                exit_points = data[(data['Long Trigger'] == 1) & (data.index > entry_point)]
                if not exit_points.empty:
                    exit_point = exit_points.index[0]
                else:
                    exit_point = data.index[-1]  # Exit at last available point
                
                entry_price = data.at[entry_point, 'Adj Close']
                exit_price = data.at[exit_point, 'Adj Close']
                pnl = -(exit_price - entry_price) / entry_price * 100.0  # Percentage PnL
            
            total_pnl += pnl
            if pnl > 0:
                win_count += 1
            
            trade_logs.append({
                'Asset': asset.ticker,
                'Strategy': type(strategy).__name__,
                'Strategy Params': strategy.params,
                'Entry Point': entry_point,
                'Entry Price': entry_price,
                'Exit Point': exit_point,
                'Exit Price': exit_price,
                'PnL': pnl
            })
        
        total_trades = len(trade_logs)

        if total_trades > 0:
            win_rate = (win_count / total_trades * 100.0)
        else:
            win_rate = 0
        
        return total_pnl, win_rate, trade_logs
