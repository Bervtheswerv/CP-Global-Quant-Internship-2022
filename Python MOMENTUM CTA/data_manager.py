import os
import pandas as pd

class DataManager():
    """
    Manages data saving and exporting operations for backtest results and trade logs.
    Attributes:
        config (Config): Configuration parameters.
    """
# ______________________________________________________________________________________________
    def __init__(self, config):
        """
        Initializes the DataManager instance.
        Parameters:
            config (Config): Configuration parameters.
        """
        self.config = config
        os.makedirs(self.config.DERIVED_DATA_DIR, exist_ok = True)
# ______________________________________________________________________________________________   
    def save_results(self, results_df, trade_logs, year):
        """
        Saves the backtest results and trade logs to Excel files.
        Parameters:
            results_df (pd.DataFrame): DataFrame containing summary results of the backtest.
            trade_logs (list of dict): List of trade log dictionaries.
            year (int): Year of the backtest.
        """
        # Convert trade logs to DataFrame
        trade_logs_df = pd.DataFrame(trade_logs)
        
        # Define file paths
        consolidated_path = os.path.join(
            self.config.DERIVED_DATA_DIR, 
            'SHORTLISTED_Consolidated_results.xlsx'
        )
        sorted_path = os.path.join(
            self.config.DERIVED_DATA_DIR, 
            'SHORTLISTED_Sorted_results.xlsx'
        )
        
        # Save results to Excel with separate sheets for each year
        with pd.ExcelWriter(consolidated_path, engine = 'openpyxl', mode = 'a' if os.path.exists(consolidated_path) else 'w') as writer:
            results_df.to_excel(writer, sheet_name = f'{year}_results', index = False)
            trade_logs_df.to_excel(writer, sheet_name = f'{year}_raw_trades', index = False)
        
        # Aggregate all years for final consolidation
        all_years = [sheet for sheet in pd.ExcelFile(consolidated_path).sheet_names if 'results' in sheet]
        combined_results = pd.DataFrame()
        
        for sheet in all_years:
            df = pd.read_excel(consolidated_path, sheet_name = sheet)
            combined_results = pd.concat([combined_results, df], ignore_index = True)
        
        # Calculate mean PnL and Win Rate
        final_df = combined_results.groupby(['Asset', 'Strategy', 'Strategy Params']).agg({
            'Total PnL': 'mean',
            'Win Rate': 'mean'
        }).reset_index()
        
        # Sort by Win Rate Mean
        sorted_df = final_df.sort_values(by='Win Rate', ascending=False)
        
        # Save consolidated and sorted results
        with pd.ExcelWriter(consolidated_path, engine = 'openpyxl', mode = 'a' if os.path.exists(consolidated_path) else 'w') as writer:
            final_df.to_excel(writer, sheet_name = 'Consolidated', index = False)
        
        with pd.ExcelWriter(sorted_path, engine = 'openpyxl', mode = 'w') as writer:
            sorted_df.to_excel(writer, sheet_name = 'Sorted', index = False)
        
        print(f"Results saved to {consolidated_path} and {sorted_path}")
