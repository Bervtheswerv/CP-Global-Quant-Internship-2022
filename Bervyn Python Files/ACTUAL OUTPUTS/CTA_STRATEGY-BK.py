import pandas as pd
import numpy as np
import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
import datetime as dt
import warnings
import glob, os, psutil, time
warnings.filterwarnings('ignore')
import talib


my_asset_list = ['AAPL', 'MSFT', 'GOOGL', 'BRK-B', 'AMZN', 'TXN', 'NVDA', 'HON', 'NTES', 'ASML', 'AMAT', 'CSCO', 'PEP', 'COST', 'ADBE', 'CMCSA', 'INTC', 'AZN', 'QCOM', 'NFLX']
# my_asset_list = ['AZN', 'QCOM', 'CSCO'] 
# ___________________________________________________________________________________________________________________________________________________________________

def CTA_Strategy(assets = my_asset_list, start = '2021-01-01', end = '2021-12-31', year = '2021', window = 14):

    # global df_all_results
    df_all_results = pd.DataFrame(columns=['Asset', 'Strategy label','Strategy Params', 'Total PnL', 'Win Rate'])  
    trade_view = []
    

    for asset in assets:
        '''A) Query price data'''

        # global asset_df
        asset_df = yf.download(tickers = asset, interval='1d', start=start, end=end, window=window)
        
        subfolder1 = f'{asset}'
        subfolder2 = f'{start} - {end}'      
        subfolder3 = f'{year}'
        subfolder_shortlisted = 'Shortlisted'
        subfolder_yearly = 'Search Data'

        '''1a) PnL Plots paths'''
        folder_path_1 = f'/Users/bervynwong/Desktop/CP Global Internship files/PnL Plots/{subfolder1}'
        folder_path_2 = f'/Users/bervynwong/Desktop/CP Global Internship files/PnL Plots/{subfolder1}/{subfolder2}'

        '''1b) SHORTLISTED PnL Plots paths'''
        folder_path_3 = f'/Users/bervynwong/Desktop/CP Global Internship files/PnL Plots/{subfolder_shortlisted}'
        folder_path_4 = f'/Users/bervynwong/Desktop/CP Global Internship files/PnL Plots/{subfolder_shortlisted}/{subfolder1}'
        folder_path_5 = f'/Users/bervynwong/Desktop/CP Global Internship files/PnL Plots/{subfolder_shortlisted}/{subfolder1}/{subfolder2}'

        '''2a) Dataframes Plots paths'''
        folder_path_6 = f'/Users/bervynwong/Desktop/CP Global Internship files/Dataframes/{subfolder_yearly}'
        folder_path_7 = f'/Users/bervynwong/Desktop/CP Global Internship files/Dataframes/{subfolder_yearly}/{subfolder3}'

        '''2b) SHORTLISTED Dataframes Plots paths'''
        folder_path_8 = f'/Users/bervynwong/Desktop/CP Global Internship files/Dataframes/{subfolder_shortlisted}'
        folder_path_9 = f'/Users/bervynwong/Desktop/CP Global Internship files/Dataframes/{subfolder_shortlisted}/{subfolder3}'


        if os.path.isdir(folder_path_1) == False: os.mkdir(folder_path_1)
        if os.path.isdir(folder_path_2) == False: os.mkdir(folder_path_2) 
        if os.path.isdir(folder_path_3) == False: os.mkdir(folder_path_3)
        if os.path.isdir(folder_path_4) == False: os.mkdir(folder_path_4)
        if os.path.isdir(folder_path_5) == False: os.mkdir(folder_path_5)
        if os.path.isdir(folder_path_6) == False: os.mkdir(folder_path_6)
        if os.path.isdir(folder_path_7) == False: os.mkdir(folder_path_7)
        if os.path.isdir(folder_path_8) == False: os.mkdir(folder_path_8)
        if os.path.isdir(folder_path_9) == False: os.mkdir(folder_path_9)


        MODE_RSI = 1 # Run RSI Strategy
        MODE_MACD = 2 # Run MACD Strategy

        '''1) RUN FOR AL PARAMETERS'''
        # STRATEGY_PARAM_RSIS = [14, 28, 32]
        # STRATEGY_PARAM_MACDS = [[12,26,9], [19,39,9], [24,52,9]]
        
        '''2) RUN FOR SHORTLISTED PARAMETERS'''
        STRATEGY_PARAM_RSIS = [14]
        STRATEGY_PARAM_MACDS = [[12, 26, 9]]
       
        '''B) Define Strategy Functions'''

        def strategy_plot(asset_df, mode, STRATEGY_PARAM_RSI, STRATEGY_PARAM_MACD):

            # Created a function to calculate RSI and MACD for each asset
            '''
            1) RSI strategy
            2) MACD Strategy
            '''        

            def calculate_RSI(df, asset, window):
                df[asset + '_RSI'] = talib.RSI(df['Adj Close'], timeperiod=window).values
                return df
                    
            def calculate_MACD(df, asset, windows):
                MACD_FAST = windows[0]
                MACD_SLOW = windows[1]
                MACD_SIGNAL = windows[2]
                df[asset + '_MACD'], df[asset + '_MACD_signal'], df[asset + '_MACD_hist'] = talib.MACD(df['Adj Close'].values, fastperiod=MACD_FAST, slowperiod=MACD_SLOW, signalperiod=MACD_SIGNAL)
                return df

    
            '''C) Generate Price Triggers'''

            asset_df = asset_df[1:] # start from second data point onwards
            
            '''Placeholder columns which you will assign the strategy to'''
            col_rsi = asset + '_RSI' # new DataFrame column called 'col_rsi'
            col_macd = asset + '_MACD' # new DataFrame column called 'col_macd'
            col_macd_hist = asset + '_MACD_hist' # new DataFrame column called 'col_macd_hist'
            col_macd_signal = asset + '_MACD_signal' # new DataFrame column called 'col_macd_signal'
            
            '''Adding important signals information into our DataFrame'''

            if mode == MODE_RSI:

                # Create buy/sell triggers
                asset_df = calculate_RSI(asset_df, asset, STRATEGY_PARAM_RSI)
                asset_df = calculate_MACD(asset_df, asset, [12,26,9]) # default MACD parameters
           
                asset_df[col_rsi + '_shift2'] = asset_df[col_rsi].shift(2)
                asset_df[col_rsi + '_shift1'] = asset_df[col_rsi].shift(1)
                asset_df[col_rsi + '_shift0'] = asset_df[col_rsi].shift(0)

                # Generating signal conditions for RSI
                asset_df['Long Trigger'] = np.where((asset_df[col_rsi + '_shift0'] > 30) & (asset_df[col_rsi + '_shift1'] <= 30), 1, 0)
                asset_df['Short Trigger'] = np.where((asset_df[col_rsi + '_shift0'] < 70) & (asset_df[col_rsi + '_shift1'] >= 70), -1, 0)


            if mode == MODE_MACD:

                # Create buy/sell triggers
                asset_df = calculate_MACD(asset_df, asset, STRATEGY_PARAM_MACD)
                asset_df = calculate_RSI(asset_df, asset, 14) # default RSI parameters

                asset_df[col_macd_hist + '_shift2'] = asset_df[col_macd_hist].shift(2)
                asset_df[col_macd_hist + '_shift1'] = asset_df[col_macd_hist].shift(1)
                asset_df[col_macd_hist + '_shift0'] = asset_df[col_macd_hist].shift(0)

                # Generating signal conditions for MACD - 9-Day EMA is the trigger line/ mean line
                asset_df['Long Trigger'] = 0
                asset_df['Short Trigger'] = 0
                asset_df.at[(asset_df[col_macd_hist + '_shift0'] > 0) & (asset_df[col_macd_hist + '_shift1'] < 0), 'Long Trigger'] = 1
                asset_df.at[(asset_df[col_macd_hist + '_shift0'] < 0) & (asset_df[col_macd_hist + '_shift1'] > 0), 'Short Trigger'] = -1 
    
# ___________________________________________________________________________________________________________________________________________________________________
            
            '''D) PnL Plot'''
            entry_points = asset_df.loc[(asset_df['Long Trigger'] > 0) | (asset_df['Short Trigger'] < 0)].index
            
            '''
            If entry: find exit
            If exit: find entry
            '''

            global total_pnl
            global pnl
            global trade_logger
            total_pnl = 0
            pnl = 0
            trade_logger = [] # captures the pnl of a particular trade made at a specific timestamp within the given timeframe

            asset_df['PnL'] = np.nan # start with a column containing non-values

            for entry_point in entry_points:
            # for every entry point, it has to find the next exit point              
                trigger_long = asset_df.loc[entry_point, 'Long Trigger']
                trigger_short = asset_df.loc[entry_point, 'Short Trigger']

                if (trigger_long > 0):
                    exit_point = asset_df.loc[(asset_df['Short Trigger'] < 0) & (asset_df.index > entry_point)]                      
                    # asset_df[asset + '_exit'] = np.where((asset_df['Short Trigger'] < 0) & (asset_df.index > entry_point), 'exit point - short', 'None')

                if (trigger_short < 0):
                    exit_point = asset_df.loc[(asset_df['Long Trigger'] > 0) & (asset_df.index > entry_point)]
                    # asset_df[asset + '_exit'] = np.where((asset_df['Long Trigger'] > 0) & (asset_df.index > entry_point), 'exit point - long', 'None')
                                    
                # if there isn't any more contrasting point, i.e. empty, then skip to the last data point (conclusive time period)
                if len(exit_point) == 0:  
                    exit_point = asset_df.index[-1]
                            
                # if not empty, use first found point
                else:
                    exit_point = exit_point.index[0]

                '''
                entry_price = asset_df.loc(entry point, price)
                exit_price = asset_df.loc(exit point, price)
                '''
                            
                entry_price = asset_df.loc[entry_point, 'Adj Close']
                exit_price = asset_df.loc[exit_point, 'Adj Close']
                            

                if trigger_long == 1:
                    pnl = 1 * (exit_price - entry_price) / entry_price * 100.0

                if trigger_short == -1:
                    pnl = -1 * (exit_price - entry_price) / entry_price * 100.0

                # print(f'Trade {entry_point}: Entry point {entry_point} at {entry_price.round(2)}, Exit point {exit_point} at {exit_price.round(2)}, PnL: {pnl.round(2)}')
                
                trade_logger.append({'Unique Asset': asset, 'Entry Point': entry_point, 'Entry Price': entry_price, 'Exit Point': exit_point, 'Exit Price': exit_price, 'PnL': pnl})  #store this in a dictionary, then consolidate it and convert it into a DataFrame

                asset_df.at[entry_point, 'PnL'] = pnl

            win_count = asset_df[asset_df['PnL'] > 0].shape[0] #win_count = len(asset_df.loc[asset_df['PnL'] > 0])
            total_count = asset_df[(asset_df['PnL'] > 0) | (asset_df['PnL'] <= 0)].shape[0] # total_count = len(asset_df.loc[(asset_df['PnL'] > 0) | (asset_df['PnL'] <= 0)])
            
            if total_count == 0: 
                win_rate = 0
                
            else: 
                win_rate = win_count / total_count * 100.0

            total_pnl = asset_df['PnL'].sum()
        
# ___________________________________________________________________________________________________________________________________________________________________
            '''E) Plotting Charts & Generate Signals'''
            
            PLOT_CHARTS = True # Turn on/off plotting of chart

            if PLOT_CHARTS == True:  
                ''' 
                Forming the template chart - depends on
                1) strategy type
                2) strategy parameters, i.e. settings
                '''
                
                '''General plotting of charts'''
                fig, (ax1,ax2,ax3) = plt.subplots(3,1, figsize=(30,20), sharex=True)
                ax1 = plt.subplot2grid(shape=(3, 1), loc=(0, 0))
                ax2 = plt.subplot2grid(shape=(3, 1), loc=(1, 0), sharex=ax1)
                ax3 = plt.subplot2grid(shape=(3, 1), loc=(2, 0), sharex=ax1)

                '''Plotting of Long/Short triggers INSIDE charts'''
                df_L = asset_df[(asset_df['Long Trigger'] == 1) & (asset_df['Long Trigger'].shift(1) == 0)]
                df_S = asset_df[(asset_df['Short Trigger'] == -1) & (asset_df['Short Trigger'].shift(1) == 0)]

                if mode == MODE_RSI:
                    
                    # PLOT CLOSING PRICES AND SIGNALS
                    ax1.set_title(label = f'{asset} - Adjusted Close Price, \n Strategy: RSI, \n Period: {STRATEGY_PARAM_RSI} Days, \n Total PnL: {total_pnl}', fontsize = 12)                
                    ax1.plot(asset_df['Adj Close'], label = 'Close Price ($USD)')
                    ax1.set_ylabel('Price in $USD')
                    ax1.scatter(df_L.index, df_L['Adj Close'], s=15**2, marker ='^', color = 'green')
                    ax1.scatter(df_S.index, df_S['Adj Close'], s=15**2, marker ='v', color = 'red')
                    ax1.legend()
                    ax1.grid() 
                    
                    # PLOT TRANSFORM DATA 1 AND SIGNALS
                    ax2.plot(asset_df[col_rsi], label = 'RSI', color = 'purple')
                    ax2.axhline(y = 30, color = 'blue', label = 'Oversold')
                    ax2.axhline(y = 70, color = 'blue', label = 'Overbought')
                    ax2.set_ylim(0,100)           
                    ax2.scatter(df_L.index, df_L[col_rsi], s=15**2, marker ='^', color = 'green')
                    ax2.scatter(df_S.index, df_S[col_rsi], s=15**2, marker ='v', color = 'red')                    
                    ax2.legend()
                    ax2.grid()

                    # PLOT TRANSFORM DATA 2 (NO SIGNALS)
                    # ax3.bar(asset_df.index, asset_df[col_macd_hist], label='Volume', color=asset_df['Positive'].map({True: 'green', False: 'red'}),width=1,alpha=0.8)
                    ax3.plot(asset_df[col_macd_hist], label = 'MACD Hist', color= 'orange')
                    ax3.plot(asset_df[col_macd], label = 'MACD', color = 'blue')
                    ax3.plot(asset_df[col_macd_signal], label = 'MACD Signal', color = 'red')
                    ax3.axhline(y = 0, color = 'black', label = 'Mid-line')
                    ax3.legend()                
                    ax3.grid()

                if mode == MODE_MACD: 
                    
                    # PLOT CLOSING PRICES AND SIGNALS
                    ax1.set_title(f'{asset} - Adjusted Close Price, \n Strategy: MACD, \n Period: {STRATEGY_PARAM_MACD}, \n Total PnL: {total_pnl}', fontsize = 12)                
                    ax1.plot(asset_df['Adj Close'], label = 'Close Price ($USD)')
                    ax1.set_ylabel('Price in $USD')
                    ax1.scatter(df_L.index, df_L['Adj Close'], s=15**2, marker ='^', color = 'green')
                    ax1.scatter(df_S.index, df_S['Adj Close'], s=15**2, marker ='v', color = 'red')
                    ax1.legend()
                    ax1.grid()

                    # PLOT TRANSFORM DATA 1 AND SIGNALS
                    # ax2.bar(asset_df.index, asset_df[col_macd_hist], label='Volume', color=asset_df['Positive'].map({True: 'green', False: 'red'}),width=1,alpha=0.8)
                    ax2.plot(asset_df[col_macd_hist], label = 'MACD Hist', color= 'orange')
                    ax2.plot(asset_df[col_macd], label = 'MACD', color = 'blue')
                    ax2.plot(asset_df[col_macd_signal], label = 'MACD Signal', color = 'red')
                    ax2.axhline(y = 0, color = 'black', label = 'Mid-line')
                    ax2.scatter(df_L.index, df_L[col_macd_hist], s=15**2, marker ='^', color = 'green')
                    ax2.scatter(df_S.index, df_S[col_macd_hist], s=15**2, marker ='v', color = 'red')
                    ax2.legend()
                    ax2.grid()

                    # PLOT TRANSFORM DATA 2 (NO SIGNALS)
                    ax3.plot(asset_df[col_rsi], label = 'RSI', color = 'purple')
                    ax3.axhline(y = 30, color = 'blue', label = 'Oversold')
                    ax3.axhline(y = 70, color = 'blue', label = 'Overbought')
                    ax3.set_ylim(0,100)
                    ax3.legend()
                    ax3.grid()

                plt.show()

# ___________________________________________________________________________________________________________________________________________________________________________
            '''
            Now we move on to the final part:
            1) Creating key columns for our final datafame we want to work with
                - in this case we are working with two dataframes: * df_all_results * & * trade_view *
            2) Saving the PnL Plots onto a png file
            '''                       
            # global strategy_label
            # global strategy_params
            strategy_label = ''
            strategy_params = ''
# ___________________________________________________________________________________________________________________________________________________________________________
            '''F) Save important DataFrames'''
            
            SAVE_DF = True  # Turn on/off saving of DataFrames

            if SAVE_DF == True:

                if mode == MODE_RSI:
                    
                    strategy_label = f'RSI_{STRATEGY_PARAM_RSI}'                       
                    strategy_params = str(STRATEGY_PARAM_RSI)+ ' Days'

                    '''SAVE FOR ALL ASSETS'''
                    # RSI_file_path = f'{folder_path_2}/{asset} - RSI_{STRATEGY_PARAM_RSI}.png' 
                    # fig.savefig(RSI_file_path)

                    '''SAVE FOR SHORTLISTED RESULTS ONLY'''
                    RSI_file_path_shortlisted = f'{folder_path_5}/{asset} - RSI_{STRATEGY_PARAM_RSI}.png'  
                    fig.savefig(RSI_file_path_shortlisted)

                if mode == MODE_MACD:
                    
                    strategy_label = f'MACD_{STRATEGY_PARAM_MACD}'
                    strategy_params = str(STRATEGY_PARAM_MACD)

                    '''1) SAVE FOR ALL ASSETS'''
                    # MACD_file_path = f'{folder_path_2}/{asset} - MACD_{STRATEGY_PARAM_MACD}.png'
                    # fig.savefig(MACD_file_path)

                    '''2) SAVE FOR SHORTLISTED RESULTS ONLY'''
                    # MACD_file_path_shortlisted = f'{folder_path_5}/{asset} - MACD_{STRATEGY_PARAM_MACD}.png'  
                    # fig.savefig(MACD_file_path_shortlisted)

                # Inserting values to the bottom of the last row of the existing DataFrame
                df_all_results.loc[len(df_all_results)] = [asset, strategy_label, strategy_params, total_pnl, win_rate]
                
                # Consolidating all the trade logs and converting it into a DataFrame, before adding it back to the main list
                trade_logger = pd.DataFrame(trade_logger) 
                trade_logger['Unique Asset'] = asset + ', ' + strategy_label + ', ' + strategy_params           
                trade_view.append(trade_logger)

        '''G) Run Strategy Combinations'''

        for STRATEGY_PARAM_RSI in STRATEGY_PARAM_RSIS:
            strategy_plot(asset_df, MODE_RSI, STRATEGY_PARAM_RSI, None)

        for STRATEGY_PARAM_MACD in STRATEGY_PARAM_MACDS:
            strategy_plot(asset_df, MODE_MACD, None, STRATEGY_PARAM_MACD)

        # trade_view = pd.concat(trade_view) # join the table to make it a full DataFrame
   
    # display(trade_view)
    # display(df_all_results)  
    '''1) RUN FOR ALL ASSETS'''
    # trade_view.to_excel(f'{folder_path_7}/{year}_raw_trades.xlsx', sheet_name = 'Raw Trades', index=False)              
    # df_all_results.to_excel(f'{folder_path_7}/{year}_results.xlsx', sheet_name = 'Results', index=False)  

    '''2) RUN FOR SHORTLISTED RESULTS ONLY'''
    # trade_view.to_excel(f'{folder_path_9}/{year}_shortlisted_raw_trades.xlsx', sheet_name = 'Shortlisted - Raw Trades', index=False)              
    # df_all_results.to_excel(f'{folder_path_9}/{year}_shortlisted_results.xlsx', sheet_name = 'Shortlisted - Results', index=False)       
# ___________________________________________________________________________________________________________________________________________________________________________
'''H) Run the function'''

CTA_Strategy(assets = my_asset_list, start = '2008-01-01', end = '2008-12-31', year = 2008, window=14)
CTA_Strategy(assets = my_asset_list, start = '2009-01-01', end = '2009-12-31', year = 2009, window=14)
CTA_Strategy(assets = my_asset_list, start = '2010-01-01', end = '2010-12-31', year = 2010, window=14)
CTA_Strategy(assets = my_asset_list, start = '2011-01-01', end = '2011-12-31', year = 2011, window=14)
CTA_Strategy(assets = my_asset_list, start = '2012-01-01', end = '2012-12-31', year = 2012, window=14)
CTA_Strategy(assets = my_asset_list, start = '2013-01-01', end = '2013-12-31', year = 2013, window=14)
CTA_Strategy(assets = my_asset_list, start = '2014-01-01', end = '2014-12-31', year = 2014, window=14)
CTA_Strategy(assets = my_asset_list, start = '2015-01-01', end = '2015-12-31', year = 2015, window=14)
CTA_Strategy(assets = my_asset_list, start = '2016-01-01', end = '2016-12-31', year = 2016, window=14)
CTA_Strategy(assets = my_asset_list, start = '2017-01-01', end = '2017-12-31', year = 2017, window=14)
CTA_Strategy(assets = my_asset_list, start = '2018-01-01', end = '2018-12-31', year = 2018, window=14)
CTA_Strategy(assets = my_asset_list, start = '2019-01-01', end = '2019-12-31', year = 2019, window=14)
CTA_Strategy(assets = my_asset_list, start = '2020-01-01', end = '2020-12-31', year = 2020, window=14)
CTA_Strategy(assets = my_asset_list, start = '2021-01-01', end = '2021-12-31', year = 2021, window=14)

# ____________________________________________________________________________________________________________________________________________
'''I) DataFrame Manipulation'''

folder_path_10 = f'/Users/bervynwong/Desktop/CP Global Internship files/Dataframes/Derived Data'

if os.path.exists(folder_path_10) == False: os.mkdir(folder_path_10)

search_paths = [f'/Users/bervynwong/Desktop/CP Global Internship files/Dataframes/Search Data/{year}/{year}_results.xlsx' for year in range(2008,2022)]
shortlisted_paths = [f'/Users/bervynwong/Desktop/CP Global Internship files/Dataframes/Shortlisted/{year}/{year}_shortlisted_results.xlsx' for year in range(2008,2022)]
datas = []

'''
Depends on two scenarios do you change the variale name:
1) search_paths, if you are runnning generic search test
2) shortlisted_paths, if you are running shortlisted results
'''
for shortlisted_path in shortlisted_paths:
    data = pd.read_excel(shortlisted_path, engine = 'openpyxl')   
    data['Key'] = data['Asset'] + ', ' + data['Strategy label'] + ', ' + data['Strategy Params'] # create a combination of columns to define one unique key column
    data.set_index('Key')
    datas.append(data)
#     display(data)
     
 
for i in range(1,len(datas)):
        datas[0] = pd.concat([datas[0], datas[i][['Total PnL', 'Win Rate']]], axis=1)

final_df = datas[0].copy()
# display(final_df)


final_df['PnL Mean'] = final_df['Total PnL'].mean(axis=1)
final_df['Win Rate Mean'] = final_df['Win Rate'].mean(axis=1)

# display(final_df)

new_column_list = [
       'Asset', 'Strategy label', 'Strategy Params', 
       '2008 PnL', '2008 Win Rate',
       'Key',
       '2009 PnL','2009 Win Rate',
       '2010 PnL','2010 Win Rate',
       '2011 PnL','2011 Win Rate',
       '2012 PnL','2012 Win Rate',
       '2013 PnL','2013 Win Rate',
       '2014 PnL','2014 Win Rate',
       '2015 PnL','2015 Win Rate',
       '2016 PnL','2016 Win Rate',
       '2017 PnL','2017 Win Rate',
       '2018 PnL','2018 Win Rate',
       '2019 PnL','2019 Win Rate',
       '2020 PnL','2020 Win Rate',
       '2021 PnL','2021 Win Rate',
       'PnL Mean','Win Rate Mean' 
       ]
# 
final_column_list = [
       'Key',
       '2008 PnL', '2009 PnL', '2010 PnL', '2011 PnL', '2012 PnL', 
       '2013 PnL', '2014 PnL', '2015 PnL', '2016 PnL', '2017 PnL', 
       '2018 PnL', '2019 PnL', '2020 PnL', '2021 PnL',
       '2008 Win Rate','2009 Win Rate','2010 Win Rate','2011 Win Rate','2012 Win Rate', 
       '2013 Win Rate','2014 Win Rate','2015 Win Rate','2016 Win Rate','2017 Win Rate', 
       '2018 Win Rate','2019 Win Rate','2020 Win Rate','2021 Win Rate', 
       'PnL Mean', 'Win Rate Mean'
        ]
# 
final_df.columns = new_column_list
final_df = final_df[final_column_list]
sorted_df = final_df.sort_values(by=['Win Rate Mean'], ascending=False)
# display(final_df)
# display(sorted_df)
# 
'''Comment out: Running a generic search test'''
# final_df.to_excel(f'{folder_path_10}/Consolidated_results.xlsx', sheet_name='Consolidated', index=False)
# sorted_df.to_excel(f'{folder_path_10}/Sorted_results.xlsx', sheet_name='Sorted', index=False)
# 
'''Comment out: Running shortlisted results'''
final_df.to_excel(f'{folder_path_10}/SHORTLISTED_Consolidated_results.xlsx', sheet_name='Consolidated', index=False)
sorted_df.to_excel(f'{folder_path_10}/SHORTLISTED_Sorted_results.xlsx', sheet_name='Sorted', index=False)