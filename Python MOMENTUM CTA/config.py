import os

class Config():
    """
    Configuration class to hold all configurable parameters for the backtesting framework.

    Attributes:
        BASE_DIR (str): The base directory where all data and plots are stored.
        PNL_PLOTS_DIR (str): Directory path for storing PnL plots.
        DATAFRAMES_DIR (str): Directory path for storing DataFrame outputs.
        DERIVED_DATA_DIR (str): Directory path for storing derived data.
        SHORTLISTED_DIR (str): Subdirectory name for shortlisted results.
        SEARCH_DATA_DIR (str): Subdirectory name for search data results.
        SCATTER_SIZE (int): Size of scatter plot markers.
        WINDOW_DEFAULT (int): Default window size for RSI calculations.
        YEARS (list): List of years for which backtesting will be performed.
        ASSET_LIST (list): List of asset tickers to be analyzed.
    """

    BASE_DIR = '/Users/bervynwong/Desktop/CP Global Internship files/'
    PNL_PLOTS_DIR = os.path.join(BASE_DIR, 'PnL Plots')
    DATAFRAMES_DIR = os.path.join(BASE_DIR, 'Dataframes')
    DERIVED_DATA_DIR = os.path.join(DATAFRAMES_DIR, 'Derived Data')
    SHORTLISTED_DIR = 'Shortlisted'
    SEARCH_DATA_DIR = 'Search Data'
    SCATTER_SIZE = 225  # 15**2
    WINDOW_DEFAULT = 14
    YEARS = list(range(2008, 2022))
    ASSET_LIST = [
        'AAPL', 'MSFT', 'GOOGL', 'BRK-B', 'AMZN', 'TXN', 'NVDA',
        'HON', 'NTES', 'ASML', 'AMAT', 'CSCO', 'PEP', 'COST',
        'ADBE', 'CMCSA', 'INTC', 'AZN', 'QCOM', 'NFLX'
    ] # Subject to change according to what assets you are focusing on
