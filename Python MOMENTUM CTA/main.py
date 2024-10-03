from config import Config
from asset import Asset
from strategies import RSIStrategy, MACDStrategy
from backtester import Backtest

def Main():
    """
    Orchestrates the backtesting workflow by initializing configurations, assets, strategies, and executing the backtest.
    """
    import warnings
    warnings.filterwarnings('ignore')  # Suppress warnings for cleaner output
    
    # Initialize configuration
    config = Config()
    
    # Initialize assets
    assets = [Asset(ticker) for ticker in config.ASSET_LIST]
    
    # Define strategy parameters
    rsi_params = [{'rsi_window': 14}]
    macd_params = [{'macd_params': [12, 26, 9]}]
    
    # Initialize strategies
    strategies = []

    for params in rsi_params:
        strategies.append(RSIStrategy(asset = None, params = params))  # asset to be set later

    for params in macd_params:
        strategies.append(MACDStrategy(asset = None, params = params))  # asset to be set later
    
    # Initialize Backtester
    backtester = Backtest(config = config, assets = assets, strategies = strategies)
    
    # Run backtest for each year (in this case  we chose 2008-2022)
    for year in config.YEARS:
        start_date = f'{year}-01-01'
        end_date = f'{year}-12-31'
        
        backtester.run_backtest(start = start_date, end = end_date, year = year, window = config.WINDOW_DEFAULT)
    
    print("Backtesting completed.")

if __name__ == "__main__":
    Main()
