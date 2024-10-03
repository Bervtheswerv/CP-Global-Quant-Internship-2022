import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

class Strategy(ABC):
    """
    Abstract base class (ABC) for trading strategies.

    Attributes:
        asset (Asset): The asset to which the strategy is applied.
        params (dict): Parameters specific to the strategy.
        signals (pd.DataFrame): DataFrame containing generated trading signals.
    """
# ______________________________________________________________________________________________
    def __init__(self, asset, params):
        """
        Initializes the Strategy instance.

        Parameters:
            asset (Asset): The asset to which the strategy is applied.
            params (dict): Parameters specific to the strategy.
        """
        self.asset = asset
        self.params = params
        self.signals = pd.DataFrame(index = self.asset.data.index)
    
    @abstractmethod
    def generate_signals(self):
        """
        Abstract method to generate trading signals based on the strategy.

        Must be implemented by all subclasses.
        """
        pass

# ______________________________________________________________________________________________
class RSIStrategy(Strategy):
    """
    Implements the Relative Strength Index (RSI) trading strategy.
    Attributes:
        MODE_RSI (int): Mode identifier for RSI strategy.
    """
    MODE_RSI = 1  # Run RSI Strategy
    # ______________________________________________________________________________________________
    def generate_signals(self):
        """
        Generates long and short trading signals based on RSI thresholds.
        Long Trigger: RSI crosses above 30.
        Short Trigger:RSI crosses below 70.
        Populates the `signals` DataFrame with 'Long Trigger' and 'Short Trigger' columns.
        Returns:
            pd.DataFrame: DataFrame containing generated signals.
        """
        window = self.params.get('rsi_window', 14)
        self.asset.calculate_rsi(window=window)
        rsi_col = f'{self.asset.ticker}_RSI'
        
        # Shifted RSI for trigger conditions
        self.asset.data[f'{rsi_col}_shift1'] = self.asset.data[rsi_col].shift(1)
        self.asset.data[f'{rsi_col}_shift0'] = self.asset.data[rsi_col].shift(0)
        
        # Generate Long and Short Triggers
        self.signals['Long Trigger'] = np.where(
            (self.asset.data[f'{rsi_col}_shift0'] > 30) & 
            (self.asset.data[f'{rsi_col}_shift1'] <= 30), 
            1, 0
        )
        self.signals['Short Trigger'] = np.where(
            (self.asset.data[f'{rsi_col}_shift0'] < 70) & 
            (self.asset.data[f'{rsi_col}_shift1'] >= 70), 
            -1, 0
        )
        
        return self.signals
    
# ______________________________________________________________________________________________
class MACDStrategy(Strategy):
    """
    Implements the Moving Average Convergence Divergence (MACD) trading strategy.
    Attributes:
        MODE_MACD (int): Mode identifier for MACD strategy.
    """
    MODE_MACD = 2  # Run MACD Strategy
    # ______________________________________________________________________________________________
    def generate_signals(self):
        """
        Generates long and short trading signals based on MACD histogram crossovers.
        Long Trigger: MACD histogram crosses above zero.
        Short Trigger: MACD histogram crosses below zero.
        Populates the `signals` DataFrame with 'Long Trigger' and 'Short Trigger' columns.
        Returns:
            pd.DataFrame: DataFrame containing the generated signals.
        """
        params = self.params.get('macd_params', [12, 26, 9])
        self.asset.calculate_macd(*params)
        macd_hist_col = f'{self.asset.ticker}_MACD_hist'
        
        # Shifted MACD Histogram for trigger conditions
        self.asset.data[f'{macd_hist_col}_shift1'] = self.asset.data[macd_hist_col].shift(1)
        self.asset.data[f'{macd_hist_col}_shift0'] = self.asset.data[macd_hist_col].shift(0)
        
        # Generate Long and Short Triggers
        self.signals['Long Trigger'] = np.where(
            (self.asset.data[f'{macd_hist_col}_shift0'] > 0) & 
            (self.asset.data[f'{macd_hist_col}_shift1'] < 0), 
            1, 0
        )
        self.signals['Short Trigger'] = np.where(
            (self.asset.data[f'{macd_hist_col}_shift0'] < 0) & 
            (self.asset.data[f'{macd_hist_col}_shift1'] > 0), 
            -1, 0
        )
        
        return self.signals
