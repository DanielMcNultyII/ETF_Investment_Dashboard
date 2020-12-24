'''
Daniel McNulty II
Last Updated: 10/2/2020

This file contains the code for the tables shown in the investment dashboard.
'''


# import plotly.graph_objs as go
import bs4
from selenium import webdriver
import chromedriver_binary


def port_tbl(ETFs):
    current_prices = []
    prior_close = []

    for ETF_Ticker in ETFs.Ticker:
        if isinstance(ETF_Ticker, (int, float)):
            current_prices.append(ETF_Ticker)
            prior_close.append(ETF_Ticker)
            continue

        is_link = 'https://finance.yahoo.com/quote/' + ETF_Ticker

        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        driver = webdriver.Chrome(options=op)

        driver.get(is_link)
        html = driver.execute_script('return document.body.innerHTML;')
        soup = bs4.BeautifulSoup(html, 'lxml')

        current_prices.append(
            [entry.text for entry in soup.find_all('span', {'class': 'Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)'})][0])
        prior_close.append(
            [entry.text for entry in soup.find_all('span', {'class': 'Trsdu(0.3s)', 'data-reactid': '44'})][1])

        driver.close()

    ETFs['Current_Price'] = [float(i) for i in current_prices]
    prior_close_float = [float(i) for i in prior_close]
    ETFs['Chg_Frm_Prior_Close'] = [round(ETFs.Current_Price[i] - prior_close_float[i], 2) for i in
                                   range(0, len(prior_close_float))]
    ETFs['Per_Chg_Frm_Prior_Close'] = [round((ETFs.Chg_Frm_Prior_Close[i] / prior_close_float[i]) * 100, 2) for i in
                                       range(0, len(prior_close_float))]
    ETFs.Per_Chg_Frm_Prior_Close = ETFs.Per_Chg_Frm_Prior_Close.astype('str') + '%'

    daily_ret = round(sum([i*j for i,j in zip(ETFs['Chg_Frm_Prior_Close'],ETFs.Weight)]),2)

    ETFs.Weight = round(ETFs.Weight * 100.0, 2)
    ETFs.Weight = ETFs.Weight.astype('str') + '%'

    ETFs.columns = ['Stock/ETF Ticker Short Name', 'Ticker', 'Investment Type', '% of Portfolio', 'Current Price',
                    'Change from Prior Close', '% Change from Prior Close']

    '''
    ETFs['CellColor'] = ['lightgreen' if i > 0 else 'lightpink' for i in ETFs.Chg_Frm_Prior_Close]
    
    layout_height = (70 * len(ETFs.ETF)) + 10

    ETFs_tbl = go.Figure(data=[go.Table(
        header=dict(values=['Stock/ETF Ticker', 'Current Price', 'Change from Prior Close',
                            '% Change from Prior Close'],
                    height=20),
        cells=dict(
            values=[ETFs.Ticker, ETFs.Current_Price, ETFs.Chg_Frm_Prior_Close, ETFs.Per_Chg_Frm_Prior_Close],
            align=['left', 'center', 'center'],
            fill_color=[ETFs.CellColor],
            height=40))],
                         layout=dict(height=layout_height))
    '''

    return ETFs[['Ticker', '% of Portfolio', 'Current Price', 'Change from Prior Close', '% Change from Prior Close']], \
           daily_ret


def his_tbl(sel_hist):
    sel_hist.sort_values(by=['Date'], inplace=True, ascending=False)

    sel_hist['GainLoss'] = round(sel_hist['Close'].diff(-1), 2)

    pergl = [round(sel_hist.GainLoss[i] / sel_hist.Close[i - 1] * 100, 3) for i in range(1, len(sel_hist.index))]
    pergl.insert(0, None)
    pergl.reverse()
    sel_hist['PerGainLoss'] = pergl
    sel_hist.PerGainLoss = sel_hist.PerGainLoss.astype(str) + '%'

    sel_hist['Date'] = sel_hist['Date'].dt.date

    sel_hist.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits',
                        'Change from Prior Close', '% Change from Prior Close']

    '''
    sel_hist['CellColor'] = ['lightgreen' if i > 0 else 'lightpink' for i in sel_hist.GainLoss]
    
    hist_tbl = go.Figure(data=[go.Table(header=dict(
                         values=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Change from Prior Close',
                                 '% Change from Prior Close']),
                         cells=dict(values=[sel_hist['Date'].dt.date, sel_hist.Open, sel_hist.High, sel_hist.Low,
                                            sel_hist.Close, sel_hist.Volume, sel_hist.GainLoss, sel_hist.PerGainLoss],
                                    fill_color=[sel_hist.CellColor]))])
    '''

    return sel_hist[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Change from Prior Close',
                     '% Change from Prior Close']]


def highlights(curr_sel):
    is_link = 'https://finance.yahoo.com/quote/' + curr_sel.info['symbol']

    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    driver = webdriver.Chrome(options=op)

    driver.get(is_link)
    html = driver.execute_script('return document.body.innerHTML;')
    soup = bs4.BeautifulSoup(html, 'lxml')

    current_price = float([entry.text for entry in
                           soup.find_all('span', {'class': 'Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)'})][0])
    prior_close = float([entry.text for entry in
                         soup.find_all('span', {'class': 'Trsdu(0.3s)', 'data-reactid': '44'})][1])
    chg_frm_prior_close = round(current_price - prior_close, 2)
    per_chg_frm_prior_close = str(round(chg_frm_prior_close/prior_close * 100, 2)) + '%'
    daily_rng = [entry.text for entry in
                 soup.find_all('td', {'class': 'Ta(end) Fw(600) Lh(14px)', 'data-test': 'DAYS_RANGE-value'})]
    yr_rng = [entry.text for entry in
              soup.find_all('td', {'class':'Ta(end) Fw(600) Lh(14px)', 'data-test':'FIFTY_TWO_WK_RANGE-value'})]
    YTD_daily_tot_ret = [entry.text for entry in
                         soup.find_all('td', {'class': 'Ta(end) Fw(600) Lh(14px)', 'data-test': 'YTD_DTR-value'})]
    exp_ratio = [entry.text for entry in
                 soup.find_all('td', {'class': 'Ta(end) Fw(600) Lh(14px)', 'data-test': 'EXPENSE_RATIO-value'})]

    high_df = {'Current Price': current_price, 'Change from Prior Close': chg_frm_prior_close,
               '% Change from Prior Close': per_chg_frm_prior_close, 'Daily Range': daily_rng, '52-Week Range': yr_rng,
               'YTD Daily Total Return': YTD_daily_tot_ret, 'Expense Ratio': exp_ratio}

    '''
    high_tbl = go.Figure(data=[go.Table(header=dict(
                         values=['Current Price', 'Change from Prior Close', '% Change from Prior Close', 'Daily Range',
                                 '52-Week Range', 'YTD Daily Total Return', 'Expense Ratio']),
                         cells=dict(values=[current_price, chg_frm_prior_close, per_chg_frm_prior_close, daily_rng,
                                            yr_rng, YTD_daily_tot_ret, exp_ratio],
                                    fill_color=[cellcolor]))])
    '''

    return high_df

