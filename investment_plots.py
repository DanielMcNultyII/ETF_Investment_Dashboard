'''
Daniel McNulty II
Last Updated: 10/2/2020

This file contains the code for the plots shown in the investment dashboard.
'''


import pandas as pd
import numpy as np
import plotly.graph_objs as go
from scipy import stats


def candle_plt(sel_hist):
    for i in ['Open', 'High', 'Close', 'Low']:
        sel_hist[i] = sel_hist[i].astype('float64')

    cndl_cht = go.Figure(data=[go.Candlestick(x=sel_hist.reset_index()['Date'],
                                              open=sel_hist['Open'],
                                              high=sel_hist['High'],
                                              low=sel_hist['Low'],
                                              close=sel_hist['Close'])])

    cndl_cht.update_layout(
        yaxis_title='Trade Price',
        xaxis_title='Date',
        margin=go.layout.Margin(
               l=0,  # left margin
               r=0,  # right margin
               b=10,  # bottom margin
               t=0,  # top margin
            ),
        )

    return cndl_cht


def lin_plt(sel_hist):
    q1, q2 = np.percentile(sel_hist.Close, [2.5, 97.5])

    xi = np.array([(sel_hist.Date[i] - sel_hist.Date[0]).days for i in range(0, len(sel_hist.Close))])
    dtp = pd.DataFrame(data={'dt': xi, 'p': sel_hist.Close})
    dtp = dtp[dtp.p > q1]
    dtp = dtp[dtp.p < q2]

    slope, intercept, r_value, p_value, std_err = stats.linregress(dtp.dt, dtp.p)
    lin_reg = slope * xi + intercept
    fin_lin_reg = pd.DataFrame(data={'Date': sel_hist.Date, 'Ols_Close': lin_reg})

    lin_cht = go.Figure(data=[go.Scatter(x=sel_hist.Date, y=sel_hist.Close, name='Close Price',
                                         line=dict(color='blue'), showlegend=False),
                              go.Scatter(x=fin_lin_reg.Date, y=fin_lin_reg.Ols_Close, name='Expected Close Price',
                                         line=dict(color='violet'), showlegend=False)])

    lin_cht.update_layout(
        yaxis_title='Close Price',
        xaxis_title='Date',
        hovermode='x',
        margin=go.layout.Margin(
            l=0,  # left margin
            r=0,  # right margin
            b=10,  # bottom margin
            t=0,  # top margin
        ),
    )

    lin_cht.update_xaxes(rangeslider_visible=True)

    return lin_cht

