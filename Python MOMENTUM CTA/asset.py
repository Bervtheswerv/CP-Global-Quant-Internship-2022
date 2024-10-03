import pandas as pd
import yfinance as yf
import talib

class Asset():
    """
    Represents a financial asset and handles data retrieval and technical indicator calculations.

    Attributes:
        ticker (str): The ticker symbol of the asset.
        data (pd.DataFrame): DataFrame containing historical price data of the asset.
    """
# ______________________________________________________________________________________________
    def __init__(self, ticker):
        """
        Initializes the Asset instance with a ticker symbol.

        Parameters:
            ticker (str): The ticker symbol of the asset (e.g., 'AAPL').
        """
        self.ticker = ticker
        self.data = pd.DataFrame()
    # ______________________________________________________________________________________________
    def fetch_data(self, start, end, interval='1d'):
        """
        Fetches historical price data for the asset using yfinance.

        Parameters:
            start (str): Start date in 'YYYY-MM-DD' format.
            end (str): End date in 'YYYY-MM-DD' format.
            interval (str, optional): Data interval (default is '1d' for daily data).

        Raises:
            Exception: If data retrieval fails.
        """
        try:
            self.data = yf.download(
                tickers = self.ticker, 
                interval = interval, 
                start = start, 
                end = end
            )

            if self.data.empty:
                print(f"Warning: No data fetched for {self.ticker} between {start} and {end}.")

        except Exception as e:
            print(f"Error fetching data for {self.ticker}: {e}")
    # ______________________________________________________________________________________________
    def calculate_rsi(self, window=14):
        """
        Calculates the Relative Strength Index (RSI) for the asset.

        Parameters:
            window (int, optional): The window size for RSI calculation (default is 14).

        Raises:
            ValueError: If 'Adj Close' column is missing in the data.
        """

        if 'Adj Close' in self.data.columns:
            self.data[f'{self.ticker}_RSI'] = talib.RSI(self.data['Adj Close'], timeperiod=window)

        else:
            raise ValueError(f"'Adj Close' column missing in data for {self.ticker}.")
    # ______________________________________________________________________________________________
    def calculate_macd(self, fast = 12, slow = 26, signal = 9):
        """
        Calculates the Moving Average Convergence Divergence (MACD) for the asset.

        Parameters:
            fast (int, optional): fast period for MACD calculation (default 12).
            slow (int, optional): slow period for MACD calculation (default 26).
            signal (int, optional): signal period for MACD calculation (default 9).

        Raises:
            ValueError: If 'Adj Close' column is missing in the data.
        """

        if 'Adj Close' in self.data.columns:
            macd, macd_signal, macd_hist = talib.MACD(
                self.data['Adj Close'], 
                fastperiod = fast, 
                slowperiod = slow, 
                signalperiod = signal
            )
            self.data[f'{self.ticker}_MACD'] = macd
            self.data[f'{self.ticker}_MACD_signal'] = macd_signal
            self.data[f'{self.ticker}_MACD_hist'] = macd_hist

        else:
            raise ValueError(f"'Adj Close' column missing in data for {self.ticker}.")