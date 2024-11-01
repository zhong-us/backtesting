import streamlit as st
from datetime import datetime, timedelta
'## Price History Trend'
st.info('For optimal viewing, use a PC or tablet or rotate your mobile device to landscape.')
'This strategy selects stocks for the portfolio based on their past performance ranking among its peers.'
'The portfolio rebalances monthly at month-end, with new stocks for the following month being selected.'
st.caption('Check back on the first day of the next month to see the new stock tickers.')
'The holding period is set for a duration of one month.'

#pool = st.selectbox('Choose pool of stocks:', ['NASDAQ-100', 'S&P 500'], label_visibility = 'visible')
'Start creating a customized portfolio by choosing a pool of stocks and then filtering them based on past performance.'
pool = st.radio('',('NASDAQ-100 (Fast)', 'S&P 500 (Slow)'),horizontal=True,label_visibility='collapsed')

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
    m = st.selectbox('months', [1,2,3,4,5,6,7,8,9,10,11,12],1,label_visibility = 'collapsed')
with col5:
    'months return.'
filters.append([n,m])

'Stocks will be held with equal weight, unless you opt for a one-stock portfolio.'
'The performance of the strategy is recorded each month for visualization.'
 
date_input = st.text_input('Strategy started from (YYYY-MM)','2024-01')

_,_,c,_,_= st.columns(5)
with c:
    run = st.button('Visualize!')

if run:
    import numpy as np
    import yfinance as yf
    import pandas as pd
    import matplotlib.ticker as ticker
    import matplotlib.pyplot as plt
    from dateutil.relativedelta import relativedelta
    import plotly.express as px

    @st.cache_data(ttl = 28800,show_spinner="Price data downloading")
    def get_price(pool,date_input):
        if pool == 'NASDAQ-100 (Fast)':
            ticker_df = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")[4]
        else:
            ticker_df = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
        tickers = ticker_df.Symbol.to_list()

        tickers = [x.replace('.','-') for x in tickers]
        plot_date = date_input+'-01'
        start_date = datetime.strptime(plot_date,'%Y-%m-%d')-relativedelta(months=13)

        df = yf.download(tickers,start=start_date,interval='1mo')['Adj Close']

        return  df


    # Tickers
    if pool == 'NASDAQ-100 (Fast)':
        idx = 'QQQ'
    else:
        idx = 'SPY'

    plot_date = date_input+'-01'
    start_date = datetime.strptime(plot_date,'%Y-%m-%d')-relativedelta(months=13)

    df = get_price(pool,date_input)

    @st.cache_data(ttl = 28800,show_spinner=False)
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

    @st.cache_data(ttl = 28800,show_spinner=False)
    def pd_pct_view(df):
        for c in df.columns:
            #df[c] = df[c].apply(lambda x: (f'{x:.2%}'))
            df.loc[:, c] = df[c].apply(lambda x: f'{x:.2%}')
        return df

    with st.spinner('Computing...'):
        # Month over month precent change
        mom = df.pct_change(fill_method=None)+1
        months_ret = [[n,return_by_m_month(mom,m)] for n,m in filters]

        returns = []
        for month in mom.index[:-1]:
            returns.append(performance(month))

        # Return of the first 12 months not consider
        returns = pd.Series(returns[12:],index=mom.index[13:])
    st.success('Computation success!')


    f'##### See how your strategy has performed since {date_input} vs. Benchmark'
    
    # Cumpound return
    cum_ret = pd.DataFrame(returns[returns.index>=plot_date].cumprod(), columns=['Strategy'])
    idx_df = yf.download(idx,start=start_date,interval='1mo')['Adj Close']
    idx_return = (idx_df.pct_change()+1)[idx_df.index>=plot_date]
    cum_ret[idx] = idx_return.cumprod()
    col1,col2 = st.columns(2)
    col1.metric('Your Cumulative Return', f'{(cum_ret.Strategy.iloc[-1]-1):.2%}')
    col2.metric(f'{idx} Cumulative Return', f'{(cum_ret[idx][-1]-1):.2%}')
    
    fig = px.line(cum_ret-1,cum_ret.index,['Strategy',idx],labels={'value':'','variable':'','Date':''})
    fig.update_layout(hovermode="x unified")
    fig.layout.yaxis.tickformat = ',.0%'
    fig.update_traces(hovertemplate = "%{y}")
    st.plotly_chart(fig)
    st.caption('Interact with the chart by hovering over it and selecting an area to enlarge. Double-click to return to full view. Use the legend to hide or show lines.')

    '##### Some statistics for monthly performance:'
    # Stats about strategy and index
    stats_df=pd.DataFrame((returns[returns.index>=plot_date]-1).describe()[1:],columns=['Strategy'])
    stats_df[idx]=(idx_return[idx_return.index>=plot_date]-1).describe()[1:]
    stats_df.index = ['Mean Monthly Return','Standard Deviation', 'Worst Monthly Return','25 Percentile Monthly Return', 'Median Monthly Return','75 Percentile Monthly Return', 'Best Monthly Return']
    st.table(pd_pct_view(stats_df.iloc[[0,1,2,4,6]]))

    #bar chart for monthly alpha: temporarily removed
    #diff = returns[returns.index>=plot_date]-idx_return[idx_return.index>=plot_date]
    #fig = px.box(diff,x= 0, points='all',title='Distribution of Monthly Alpha',labels={'0':''})
    #fig.update_traces(hovertemplate = "%{x}")
    #fig.layout.xaxis.tickformat = '.2%'
    #st.plotly_chart(fig,use_container_width=True)
    #'[Alpha](https://en.wikipedia.org/wiki/Alpha_(finance)) represents the excess return, or the degree by which your strategy outperforms the market.'

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
    daily_cumprod = pd.concat([tmp,(daily_cumprod-1)])
    fig = px.line(daily_cumprod,daily_cumprod.index,['Strategy',idx],labels={'index':'', 'value':'','variable':''},title='Current Month Cumulative Return')
    fig.update_layout(hovermode="x unified")
    fig.update_traces(hovertemplate = "%{y}")
    fig.layout.yaxis.tickformat = '.2%'
    st.plotly_chart(fig)

    # Yahoo bug
    with st.expander('If the chart appears inaccurate at the beginning of a month, click here for info on a bug in Yahoo Finance.'):
        st.caption('''Real-time financial data from Yahoo Finance may occasionally have discrepancies, 
        such as missing values on the 31st day of a month or mislabeling the first day of a new month 
        as the last day of the previous month. These issues can affect the accuracy of percentage 
        calculations and visualizations, especially when transitioning from one month to the next.
         These issues are typically fixed by Yahoo within a day or two. If the plot appears suspicious, or 
         if data from a previous month is still present when it's already a new month, please check back later for corrected data.''')


    '##### Daily performance of chosen stocks for current month:'
    monthly_df = (mom-1).loc[current:,top_tickers][1:]
    monthly_df.index = ['Current Month total return']
    monthly_df = pd.concat([daily_df[top_tickers],monthly_df])
    st.table(pd_pct_view(monthly_df))