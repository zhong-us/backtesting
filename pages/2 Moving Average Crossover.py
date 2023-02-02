import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime,timedelta

'## Moving Average Crossover'
'This strategy is a popular trading approach that uses two moving averages (fast and slow) to generate buy and sell signals.'
st.caption('Moving average is a commonly used technical analysis indicator that calculates the average price of an asset over a specified number of periods.')
'The strategy works by comparing the fast moving average (representing short-term momentum) with the slow moving average (representing long-term momentum).'
'When the fast moving average crosses above the slow moving average, it generates a buy signal, indicating that the trend is bullish and that the price is likely to continue to rise.'
'Conversely, when the fast moving average crosses below the slow moving average, it generates a sell signal, indicating that the trend is bearish and that the price is likely to continue to fall.'
'This strategy is a lagging approach that follows the market rather than leading it. As a result, rapid upward movements in the market may not be captured, and quick downward movements may not be avoided.'
'The strategy implements trades on the close of each day when a signal is generated. It is possible to amplify the strategy by opting to "double down" and short the asset when a sell signal is confirmed.'

# calculate moving average crossover
def moving_average_cross(data, fast_avg, slow_avg):
    short_rolling = data.rolling(window=fast_avg).mean()
    long_rolling = data.rolling(window=slow_avg).mean()
    signals = np.where(short_rolling > long_rolling, 1, -1)
    return np.roll(signals,1)

ticker = st.text_input('Please input **one** stock/ETF ticker (Eg. BRK-B) for visualization:')
plot_date = st.date_input("Visualization starting from",value=datetime(2020,1,1),max_value=datetime.today()-timedelta(days=5))
short = st.checkbox('"Double down" by shorting the same quantity of the asset when a sell signal is triggered.')
fast_avg = st.slider('Fast Moving Average', 5, 250, 50,format='%d days')
slow_avg = st.slider('Slow Moving Average', 10, 1000, 200,format='%d days')
if ticker:    
    # in order for visualization to start on the plot_date
    # analysis has to start earlier to calculate the moving averages
    # and to compensate for weekends and holidays
    start_date = plot_date-timedelta(days=slow_avg*1.5)
    data = yf.download(ticker, start=start_date)['Adj Close'].pct_change()+1
    if data.shape[0] == 0:
        st.error('Please input a valid ticker.')
    else:
        signals = moving_average_cross(data, fast_avg, slow_avg)
        portfolio = data * signals
        if not short:
            portfolio_return = portfolio.loc[(portfolio>0)&(portfolio.index.date>=plot_date)].cumprod().dropna()
        else:
            portfolio.loc[(portfolio<0)] = 2+portfolio.loc[(portfolio<0)]
            portfolio_return = portfolio.loc[portfolio.index.date>=plot_date].cumprod().dropna()
        df = pd.DataFrame(data.loc[data.index.date>=plot_date].cumprod())
        df.columns = [ticker]
        df['Strategy']=portfolio_return

        #st.line_chart(df)

        fig,ax=plt.subplots(figsize=(10,6))
        plt.plot(df)
        ax.grid()
        ax.set_title('Strategy vs. underlying asset')
        ax.legend(df.columns)
        st.pyplot(fig)