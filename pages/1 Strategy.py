import streamlit as st

st.info('If you are viewing from a phone, horizontal view is recommended.')
'This strategy will choose the stocks to hold based on past performance.'
'Holding period is for one whole month.'
'If you have more than 1 stock in your portfolio (strongly recommend), stocks will be held as equal weight.'
'Rebalances happen on close of each month when new tickers for next month will be determined.'
'You can choose a pool of stocks and filter them based on their past performance as you like.'
'The portfolio performance for each month will be saved and used for visualization.'
pool = st.selectbox('Choose pool of stocks:', ['NASDAQ-100', 'SP-500'], label_visibility = 'visible')


'You can filter them multiple times to determine the ones having the strongest momentum.'
st.caption('If less than 4 filters is desired, you can use the same number of stocks as your last filtering for the filters that\'re not needed. For example, if only 3 filters are needed, and you need 10 stocks in your portfolio, just put 10 stocks in your 4th filter as well and don\'t worry about the month options.')
# list of lists of # of stocks to stay and # of months to look back
# filters = [[n,m],[n,m],[n,m],[n,m]]
filters = []
# 1st filter
col1,col2,col3,col4,col5 = st.columns(5)
with col1:
    'Get the top'
with col2:
    n = st.selectbox('numbers',[1,2,3,4,5,10,20,30,40,50,60,70,80,90,100,200,250],index = 9,label_visibility = 'collapsed')
with col3:
    'in them using past'
with col4:
    m = st.selectbox('months', [1,2,3,4,5,6,7,8,9,10,11,12],index = 11,label_visibility = 'collapsed')
with col5:
    'months return'
filters.append([n,m])

# 2nd filter
col1,col2,col3,col4,col5 = st.columns(5)
with col1:
    'Then get the top'
with col2:
    n = st.selectbox('numbers',[1,2,3,4,5,10,20,30,40,50,60,70,80,90,100,200,250],index = 7,label_visibility = 'collapsed')
with col3:
     'in them using past'
with col4:
    m = st.selectbox('months', [1,2,3,4,5,6,7,8,9,10,11,12], 5,label_visibility = 'collapsed')
with col5:
    'months return'
filters.append([n,m])

# 3rd filter
col1,col2,col3,col4,col5 = st.columns(5)
with col1:
    'Then get the top'
with col2:
    n = st.selectbox('numbers',[1,2,3,4,5,10,20,30,40,50,60,70,80,90,100,200,250],5,label_visibility = 'collapsed')
with col3:
    'in them using past'
with col4:
    m = st.selectbox('months', [1,2,3,4,5,6,7,8,9,10,11,12],2,label_visibility = 'collapsed')
with col5:
    'months return'
filters.append([n,m])

# 4th filter
col1,col2,col3,col4,col5 = st.columns(5)
with col1:
    'Then get the top'
with col2:
    n = st.selectbox('numbers',[1,2,3,4,5,10,20,30,40,50,60,70,80,90,100,200,250],1,label_visibility = 'collapsed')
with col3:
    'in them using past'
with col4:
    m = st.selectbox('months', [1,2,3,4,5,6,7,8,9,10,11,12],0,label_visibility = 'collapsed')
with col5:
    'months return.'
filters.append([n,m])

#st.text_input('Input ploting start date (YYYY-MM)')

_,_,c,_,_= st.columns(5)
with c:
    run = st.button('Visualize!')

if run:
    import numpy as np
    import yfinance as yf
    import pandas as pd

    # Tickers
    if pool == 'NASDAQ-100':
        ticker_df = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")[4]
        tickers = ticker_df.Ticker.to_list()
        idx = 'QQQ'
    else:
        ticker_df = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
        tickers = ticker_df.Symbol.to_list()
        idx = 'SPY'

    
    # backtest start date
    # to be adjustable by user in the future
    start_date = '2011-12-01'

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

        # Return of 1st year might not be accurate
        returns = pd.Series(returns[12:],index=mom.index[13:])
    st.success('Computation success!')


    '#### See how your portfolio performed in past 10 years compare to index'

    plot_date='2013-01-01'
    
    # Cumpound return
    cum_ret = pd.DataFrame(returns[returns.index>=plot_date].cumprod(), columns=['Portfolio'])
    idx_df = yf.download(idx,start=start_date,interval='1mo')['Adj Close']
    idx_return = (idx_df.pct_change()+1)[idx_df.index>=plot_date]
    cum_ret[idx] = idx_return.cumprod()
    col1,col2 = st.columns(2)
    col1.metric('Your Return', f'{100 * cum_ret.Portfolio[-1]:.2f}%')
    col2.metric(f'{idx} Return', f'{100*cum_ret[idx][-1]:.2f}%')
    st.line_chart(cum_ret)


    '#### What\'s your monthly Alpha compare to index?'
    st.caption('Alpha means the excess return / the amount that you \'beat the market\'')
    # Difference between strategy and index (Alpha)
    import matplotlib.ticker as ticker
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax = ((returns[returns.index>=plot_date]-idx_return[idx_return.index>=plot_date])*100).plot(kind='box', vert=False ,grid=True, figsize = (8,4))
    ax.xaxis.set_major_formatter(ticker.PercentFormatter())
    st.pyplot(fig)

    current = mom.index[-2]
    monthly_df = (mom-1).loc[current:,get_top(current)]
    monthly_df['Portfolio'] = monthly_df.mean(axis=1)
    monthly_df[idx]=idx_return[current:]-1
    monthly_df.index = ['Last Month', 'This Month total']

    # Portfolio returns daily
    daily_df = yf.download(get_top(current).to_list(),start=current)['Adj Close'].pct_change().loc[mom.index[-1]:]
    daily_df['Portfolio'] = daily_df.mean(axis=1)
    daily_df[idx] = yf.download(idx,start=current)['Adj Close'].pct_change().loc[mom.index[-1]:]
    daily_df.index = [x.date() for x in daily_df.index]
    monthly_df = pd.concat([monthly_df.iloc[[-2]],daily_df,monthly_df.iloc[[-1]]])
    
    '#### How is it performing for current month?'
    # Daily chart 
    fig, ax = plt.subplots()
    daily_cumprod = (daily_df[['Portfolio',idx]]+1).cumprod()
    tmp = pd.DataFrame([[0,0]],columns=['Portfolio',idx],index=[(mom.index[-1]-pd.DateOffset(1)).date()])
    pd.concat([100*(daily_cumprod-1),tmp]).plot(ax=ax,grid=True,title=f'Performance since {mom.index[-1].date()}',figsize=(8,5))
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    st.pyplot(fig)


    '#### Stock tickers for current month and daily comparison with index:'
    with st.expander('This is not financial advice. Please click with caution'):
        st.table(monthly_df)