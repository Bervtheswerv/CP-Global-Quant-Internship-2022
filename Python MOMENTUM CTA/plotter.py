from strategy import RSIStrategy, MACDStrategy
import os
import pandas as pd
import matplotlib.pyplot as plt

class Plotter():
    """
    Handles plotting of price data, indicators, and trading signals.
    Attributes:
        config (Config): Configuration parameters.
        asset (Asset): The asset being plotted.
        strategy (Strategy): The strategy applied.
        trades (list of dict): Detailed trade logs.
        pnl (float): Total PnL for the strategy.
        year (int): Year of the backtest.
    """
# ______________________________________________________________________________________________
    def __init__(self, config, asset, strategy, trades, pnl, year):
        """
        Initializes the Plotter instance.
        Parameters:
            config (Config): Configuration parameters.
            asset (Asset): The asset being plotted.
            strategy (Strategy): The strategy applied.
            trades (list of dict): Detailed trade logs.
            pnl (float): Total PnL for the strategy.
            year (int): Year of the backtest.
        """
        self.config = config
        self.asset = asset
        self.strategy = strategy
        self.trades = trades
        self.pnl = pnl
        self.year = year
# ______________________________________________________________________________________________
    def plot_and_save(self):
        """
        Generates and saves plots for the strategy and asset.
        Plots include:
            - Adjusted Close Price with Buy/Sell triggers.
            - RSI or MACD indicators based on the strategy.
            - MACD or RSI indicator complementary to the strategy.
        Saves plots to the designated directories based on configuration.
        """
        PLOT_CHARTS = True  # Toggle plotting
        SAVE_PLOTS = True   # Toggle saving plots
        
        if not PLOT_CHARTS:
            return
        
        data = self.asset.data.copy()
        signals = self.strategy.signals
        
        # Merge signals with data
        data = data.join(signals)
        
        # Identify trade entry and exit points for plotting
        trade_entries = pd.DataFrame(self.trades).set_index('Entry Point')
        trade_exits = pd.DataFrame(self.trades).set_index('Exit Point')
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize = (15, 10), sharex = True)
        
        # Plot Adjusted Close Price
        ax1.plot(data['Adj Close'], label = 'Adj Close Price')
        ax1.set_title(
            f"{self.asset.ticker} - {type(self.strategy).__name__} Strategy ({self.year})\nTotal PnL: {self.pnl:.2f}%",
            fontsize=12
        )
        ax1.set_ylabel('Price ($USD)')
        ax1.legend()
        ax1.grid(True)
        
        # Plot Buy/Sell Signals
        ax1.scatter(
            trade_entries['Entry Point'], 
            trade_entries['Entry Price'], 
            marker = '^', 
            color = 'green', 
            label = 'Buy Trigger', 
            s = self.config.SCATTER_SIZE
        )
        ax1.scatter(
            trade_exits['Exit Point'], 
            trade_exits['Exit Price'], 
            marker = 'v', 
            color = 'red', 
            label = 'Sell Trigger', 
            s = self.config.SCATTER_SIZE
        )
        ax1.legend()
        
        # Plot RSI or MACD based on strategy
        if isinstance(self.strategy, RSIStrategy):
            rsi_col = f"{self.asset.ticker}_RSI"
            ax2.plot(data[rsi_col], label = 'RSI', color = 'purple')
            ax2.axhline(30, color = 'blue', linestyle = '--', label = 'Oversold')
            ax2.axhline(70, color = 'blue', linestyle = '--', label = 'Overbought')
            ax2.set_ylabel('RSI')
            ax2.legend()
            ax2.grid(True)
            
            # Plot MACD on ax3
            macd_hist_col = f"{self.asset.ticker}_MACD_hist"
            macd_col = f"{self.asset.ticker}_MACD"
            macd_signal_col = f"{self.asset.ticker}_MACD_signal"
            ax3.plot(data[macd_hist_col], label = 'MACD Histogram', color = 'orange')
            ax3.plot(data[macd_col], label = 'MACD', color = 'blue')
            ax3.plot(data[macd_signal_col], label = 'MACD Signal', color = 'red')
            ax3.axhline(0, color = 'black', linestyle = '--')
            ax3.set_ylabel('MACD')
            ax3.legend()
            ax3.grid(True)
        
        elif isinstance(self.strategy, MACDStrategy):
            macd_hist_col = f"{self.asset.ticker}_MACD_hist"
            macd_col = f"{self.asset.ticker}_MACD"
            macd_signal_col = f"{self.asset.ticker}_MACD_signal"
            ax2.plot(data[macd_hist_col], label = 'MACD Histogram', color = 'orange')
            ax2.plot(data[macd_col], label = 'MACD', color = 'blue')
            ax2.plot(data[macd_signal_col], label = 'MACD Signal', color = 'red')
            ax2.axhline(0, color = 'black', linestyle = '--')
            ax2.set_ylabel('MACD')
            ax2.legend()
            ax2.grid(True)
            
            # Plot RSI on ax3
            rsi_col = f"{self.asset.ticker}_RSI"
            ax3.plot(data[rsi_col], label = 'RSI', color = 'purple')
            ax3.axhline(30, color = 'blue', linestyle = '--', label = 'Oversold')
            ax3.axhline(70, color = 'blue', linestyle = '--', label = 'Overbought')
            ax3.set_ylabel('RSI')
            ax3.legend()
            ax3.grid(True)
        
        plt.xlabel('Date')
        plt.tight_layout()
        
        if SAVE_PLOTS:
            # Define folder paths
            subfolder1 = self.asset.ticker
            subfolder2 = f"{self.config.SEARCH_DATA_DIR}/{self.year}"
            subfolder_shortlisted = self.config.SHORTLISTED_DIR
            
            # Create directories if they don't exist
            os.makedirs(
                os.path.join(self.config.PNL_PLOTS_DIR, subfolder1, subfolder2), 
                exist_ok = True
            )
            os.makedirs(
                os.path.join(
                    self.config.PNL_PLOTS_DIR, 
                    subfolder_shortlisted, 
                    subfolder1, 
                    subfolder2
                ), 
                exist_ok = True
            )
            
            # Define file path
            if isinstance(self.strategy, RSIStrategy):
                strategy_label = f"RSI_{self.strategy.params.get('rsi_window', 14)}"
                strategy_params = f"{self.strategy.params.get('rsi_window', 14)} Days"
            elif isinstance(self.strategy, MACDStrategy):
                strategy_label = f"MACD_{'_'.join(map(str, self.strategy.params.get('macd_params', [12, 26, 9])))}"
                strategy_params = f"{self.strategy.params.get('macd_params', [12, 26, 9])}"
            else:
                strategy_label = "Unknown_Strategy"
                strategy_params = "N/A"
            
            filename = f"{self.asset.ticker} - {strategy_label}.png"
            save_path = os.path.join(
                self.config.PNL_PLOTS_DIR, 
                subfolder_shortlisted, 
                subfolder1, 
                subfolder2, 
                filename
            )
            
            # Save the plot
            plt.savefig(save_path)
            plt.close()
            print(f"Plot saved to {save_path}")
        
        else:
            plt.show()
