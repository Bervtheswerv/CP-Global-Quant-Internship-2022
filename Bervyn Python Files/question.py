  '''
  For generating conditions, in order for a particular dataframe 
  to fill either values,
  which method is more efficient?
  np.where() OR pd.at()?
  '''
  
#   1) np.where()
  if method == MODE_RSI:

 

    # Generating signal conditions for RSI
    asset_df['Long Trigger'] = np.where((asset_df[col_rsi + '_shift0'] > 30) & (asset_df[col_rsi + '_shift1'] <= 30), 1, 0)

    asset_df['Short Trigger'] = np.where((asset_df[col_rsi + '_shift0'] < 70) & (asset_df[col_rsi + '_shift1'] >= 70), -1, 0)


# __________# __________# __________# __________# __________# __________# __________# __________# __________# __________# __________# __________
#   2) pd.at()

    asset_df['Long Trigger'] = 0
    asset_df['Short Trigger'] = 0

    # Long signal - capture turning points about the 9-day EMA mean line, i.e. U-shape turning point
    asset_df.at[
            (asset_df[col_macd_hist + '_shift0'] > 30) & (asset_df[col_macd_hist + '_shift1'] <= 30), 
            'Long Trigger'] = 1

    # Short signal - capture turning points about the 9-day EMA mean line, i.e. n-shape turning point
    asset_df.at[
            (asset_df[col_macd_hist + '_shift0'] < 70) & (asset_df[col_macd_hist + '_shift1'] >= 70),
            'Short Trigger'] = -1
