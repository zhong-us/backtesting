import streamlit as st
from datetime import datetime, timedelta
'## Price History Trend'
st.info('For optimal viewing on mobile, rotate your device to landscape orientation.')
'This strategy selects stocks for the portfolio based on their past performance ranking among its peers.'
'The portfolio rebalances monthly at month-end, with new stocks for the following month being selected.'
st.caption('Check back on the first day of the next month to see the new stock tickers.')
'The holding period is set for a duration of one month.'

#pool = st.selectbox('Choose pool of stocks:', ['NASDAQ-100', 'S&P 500'], label_visibility = 'visible')
pool = st.radio('Create a customized portfolio choosing a pool of stocks and filtering them based on past performance.'
        ,('NASDAQ-100 (Fast)', 'S&P 500 (Slow)'),horizontal=True)

'Multiple rounds of filtering can be applied to identify stocks with the strongest momentum.'
st.caption('If less than 4 filters are needed, put the final number of stocks left in the filters that\'re not needed. For example, if only 3 filters are needed, and you need 10 stocks in your portfolio, just put 10 stocks in your 4th filter as well and choose any month option (It does not matter).')
# list of lists of # of stocks to stay and # of months to look back
# filters = [[n,m],[n,m],[n,m],[n,m]]
filters = []
# 1st filter
col1,col2,col3,col4,col5 = st.columns(5)
with col1:
    'Find the top'
with col2:
    n = st.selectbox('numbers',[1,2,3,4,5,10,20,30,40,50,60,70,80,90,100,200,250],index = 9,label_visibility = 'collapsed')
with col3:
    'performers using'
with col4:
    m = st.selectbox('months', [1,2,3,4,5,6,7,8,9,10,11,12,18,24],index = 11,label_visibility = 'collapsed')
with col5:
    'months return'
filters.append([n,m])

# 2nd filter
col1,col2,col3,col4,col5 = st.columns(5)
with col1:
    'Then find the top'
with col2:
    n = st.selectbox('numbers',[1,2,3,4,5,10,20,30,40,50,60,70,80,90,100,200,250],index = 7,label_visibility = 'collapsed')
with col3:
     'performers using'
with col4:
    m = st.selectbox('months', [1,2,3,4,5,6,7,8,9,10,11,12,18], 5,label_visibility = 'collapsed')
with col5:
    'months return'
filters.append([n,m])

# 3rd filter
col1,col2,col3,col4,col5 = st.columns(5)
with col1:
    'Then find the top'
with col2:
    n = st.selectbox('numbers',[1,2,3,4,5,10,20,30,40,50,60,70,80,90,100,200,250],5,label_visibility = 'collapsed')
with col3:
    'performers using'
with col4:
    m = st.selectbox('months', [1,2,3,4,5,6,7,8,9,10,11,12],2,label_visibility = 'collapsed')
with col5:
    'months return'
filters.append([n,m])

# 4th filter
col1,col2,col3,col4,col5 = st.columns(5)
with col1:
    'Then find the top'
with col2:
    n = st.selectbox('numbers',[1,2,3,4,5,10,20,30,40,50,60,70,80,90,100,200,250],1,label_visibility = 'collapsed')
with col3:
    'performers using'
with col4:
    m = st.selectbox('months', [1,2,3,4,5,6,7,8,9,10,11,12],0,label_visibility = 'collapsed')
with col5:
    'months return.'
filters.append([n,m])

'Stocks will be held with equal weight, unless you opt for a one-stock portfolio.'
'The performance of the strategy is recorded each month for visualization.'
 
date_input = st.text_input('Visualization start from (YYYY-MM)','2013-01')

_,_,c,_,_= st.columns(5)
with c:
    run = st.button('Visualize!')

if run:
    import numpy as np
    import yfinance as yf
    import pandas as pd
    import matplotlib.ticker as ticker
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from dateutil.relativedelta import relativedelta

    # Tickers
    if pool == 'NASDAQ-100 (Fast)':
        ticker_df = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")[4]
        tickers = ticker_df.Ticker.to_list()
        idx = 'QQQ'
    else:
        ticker_df = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
        tickers = ticker_df.Symbol.to_list()
        idx = 'SPY'

    tickers = [x.replace('.','-') for x in tickers]
    plot_date = date_input+'-01'
    start_date = datetime.strptime(plot_date,'%Y-%m-%d')-relativedelta(months=13)

    with st.spinner('Data Downloading...'):
        df = yf.download(tickers,start=start_date,interval='1mo')['Adj Close']
    st.success('Download success!')

    def return_by_m_month(df,m):
        return df.rolling(m).apply(np.prod)

    def get_top(month):
        top = mom.columns
        for n,ret in months_ret:
            top = ret.loc[month,top].nlargest(n).index
        return top

    def performance(month):
        portfolio = mom.loc[month:,get_top(month)][1:2] # next month performance
        return portfolio.mean(axis=1).values[0]

    with st.spinner('Computing...'):
        # Month over month precent change
        mom = df.pct_change()+1
        months_ret = [[n,return_by_m_month(mom,m)] for n,m in filters]

        returns = []
        for month in mom.index[:-1]:
            returns.append(performance(month))

        # Return of the first 12 months not consider
        returns = pd.Series(returns[12:],index=mom.index[13:])
    st.success('Computation success!')


    f'#### See how your strategy has performed since {date_input} vs. index'
    
    # Cumpound return
    cum_ret = pd.DataFrame(returns[returns.index>=plot_date].cumprod(), columns=['Strategy'])
    idx_df = yf.download(idx,start=start_date,interval='1mo')['Adj Close']
    idx_return = (idx_df.pct_change()+1)[idx_df.index>=plot_date]
    cum_ret[idx] = idx_return.cumprod()
    col1,col2 = st.columns(2)
    col1.metric('Your Return', f'{100 * cum_ret.Strategy[-1]:.2f}%')
    col2.metric(f'{idx} Return', f'{100*cum_ret[idx][-1]:.2f}%')
    #st.line_chart(cum_ret)
    fig, ax = plt.subplots()
    (100*cum_ret).plot(ax=ax,figsize=(8,6))
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    ax.set_ylabel('Return')
    ax.grid()
    ax.set_title(f'Cumulated return')
    ax.legend(['Strategy',idx])
    st.pyplot(fig)

    '#### Some statistics for monthly performance:'
    # Stats about strategy and index
    stats_df=pd.DataFrame((returns[returns.index>=plot_date]-1).describe()[1:],columns=['Strategy'])
    stats_df[idx]=(idx_return[idx_return.index>=plot_date]-1).describe()[1:]
    stats_df.index = ['Mean Monthly Return','Standard Deviation', 'Worst Monthly Return','25 Percentile Monthly Return', 'Medium Monthly Return','75 Percentile Monthly Return', 'Best Monthly Return']
    st.table(stats_df)

    '#### What\'s your monthly Alpha compare to index?'
    st.caption('Alpha represents the excess return, or the degree by which your strategy outperforms the market.')
    # Difference between strategy and index (Alpha)
    fig, ax = plt.subplots()
    ax = ((returns[returns.index>=plot_date]-idx_return[idx_return.index>=plot_date])*100).plot(kind='box', vert=False ,grid=True, figsize = (8,4))
    ax.xaxis.set_major_formatter(ticker.PercentFormatter())
    st.pyplot(fig)


    '#### Closer look for current month:'
    current = mom.index[-2]
    
    # Portfolio returns daily
    top_tickers = get_top(current).to_list()
    daily_df = yf.download(top_tickers,start=current)['Adj Close'].pct_change().loc[mom.index[-1]:]
    if len(top_tickers)==1: # daily_df is a Series
        daily_df = daily_df.to_frame(*top_tickers)
    daily_df['Strategy'] = daily_df.mean(axis=1)
    daily_df[idx] = yf.download(idx,start=current)['Adj Close'].pct_change().loc[mom.index[-1]:]
    daily_df.index = [x.date() for x in daily_df.index]
    
    # Daily chart 
    fig, ax = plt.subplots()
    daily_cumprod = (daily_df[['Strategy',idx]]+1).cumprod()
    tmp = pd.DataFrame([[0,0]],columns=['Strategy',idx],index=[(mom.index[-1]-pd.DateOffset(1)).date()])
    pd.concat([100*(daily_cumprod-1),tmp]).plot(ax=ax,grid=True,title=f'Performance since {mom.index[-1].date()}',figsize=(14,8))
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    st.pyplot(fig)

    # Yahoo bug
    with st.expander('If the chart appears inaccurate at the beginning of a month, click here for info on a bug in Yahoo Finance.'):
        st.caption('''Real-time financial data from Yahoo Finance may occasionally have discrepancies, 
        such as missing values on the 31st day of a month or mislabeling the first day of a new month 
        as the last day of the previous month. These issues can affect the accuracy of percentage 
        calculations and visualizations, especially when transitioning from one month to the next.
         These issues are typically fixed by Yahoo within a day or two. If the plot appears suspicious, or 
         if data from a previous month is still present when it's already a new month, please check back later for corrected data.''')


    '#### Daily performance of chosen stocks for current month:'
    monthly_df = (mom-1).loc[current:,top_tickers][1:]
    monthly_df.index = ['Current Month total return']
    monthly_df = pd.concat([daily_df[top_tickers],monthly_df])
    st.table(monthly_df)