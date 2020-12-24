'''
Daniel McNulty II
Last Updated: 10/2/2020

This file contains the code for the investment dashboard itself.
'''

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
from dash.dependencies import Input, Output, State
import base64
import datetime
import io
import pandas as pd
import yfinance as yf
from dateutil.relativedelta import relativedelta
from datetime import datetime
import investment_tables as it
import investment_plots as ip


app = dash.Dash(__name__, prevent_initial_callbacks=True)
app.layout = html.Div(children=[
    html.Div(className='column1', children=[
             html.H1('Portfolio'),
             dcc.Loading(id='load-port', children=[
                 html.H2(id='curr_val_chg'),
                 dash_table.DataTable(
                                  id='portfolio_values',
                                  style_cell={
                                      'textAlign': 'center',
                                      'whiteSpace': 'normal',
                                      'height': 'auto',
                                      'width': '20%',
                                      'color': 'white',
                                      'backgroundColor': '#696969',
                                  },
                                  style_header={'backgroundColor': '#000000'},
                                  style_cell_conditional=[
                                  {
                                     'if': {'column_id': 'Ticker'},
                                        'textAlign': 'left',
                                        'width': '10%',
                                  },
                                  {
                                     'if': {'column_id': '% of Portfolio'},
                                        'width': '10%',
                                  },
                                  ],
                                  style_data_conditional=[
                                    {
                                        'if': {
                                            'filter_query': '{{Change from Prior Close}} < {}'.format(0.00),
                                        },
                                        'backgroundColor': '#FF4136',
                                    },
                                    {
                                       'if': {
                                            'filter_query': '{{Change from Prior Close}} > {}'.format(0.00),
                                          },
                                       'backgroundColor': '#3cb371',
                                    },
                                    {
                                        'if': {
                                            'state': 'active'  # 'active' | 'selected'
                                        },
                                        'backgroundColor': '#696969',
                                        'border': '#ffffff',
                                    }
                                  ],
                                  style_as_list_view=True,
                 ),
                 dbc.Button("Refresh Portfolio", id="Refresh-Portfolio")], type='circle'),
                 dcc.Upload(
                     id='upload-data',
                     children=html.Div([
                         'Drag & Drop or ',
                         html.A('Select File')
                     ]),
                     style={
                         'width': '90%',
                         'height': '60px',
                         'lineHeight': '60px',
                         'borderWidth': '1px',
                         'borderStyle': 'dashed',
                         'borderRadius': '5px',
                         'textAlign': 'center',
                         'margin': '10px'
                     },
                     # Allow multiple files to be uploaded
                     multiple=False
                ),
            ]),
    html.Div(className='column2', children=[
             html.Div(children=[
                 html.H1('ETF Lookup'),
                 dcc.Dropdown(
                        id='invest_select',
                        clearable=False,
                        placeholder='Select Stock/ETF',
                 )]
             ),
             html.H2('Current Info'),
             dcc.Loading(id='load-hl', children=[dash_table.DataTable(
                                  id='daily_highlights',
                                  style_cell={
                                      'textAlign': 'center',
                                      'whiteSpace': 'normal',
                                      'height': 'auto',
                                      'color': 'white',
                                      'backgroundColor': '#696969',
                                  },
                                  style_header={'backgroundColor': '#000000'},
                                  style_data_conditional=[
                                      {
                                         'if': {
                                             'filter_query': '{{Change from Prior Close}} < {}'.format(0.00),
                                         },
                                         'backgroundColor': '#FF4136',
                                      },
                                      {
                                         'if': {
                                             'filter_query': '{{Change from Prior Close}} > {}'.format(0.00),
                                         },
                                         'backgroundColor': '#3cb371',
                                      },
                                      {
                                          'if': {
                                              'state': 'active'  # 'active' | 'selected'
                                          },
                                          'backgroundColor': '#696969',
                                          'border': '#ffffff',
                                      }
                                  ],
                                  style_as_list_view=True,
                )], type='circle'
             ),
             html.H2('Historic Data'),
             dcc.RadioItems(id='graph_type',
                            options=[
                                 {'label': 'Candle', 'value': 'Candle'},
                                 {'label': 'Line', 'value': 'Line'},
                            ],
                            value='Line'
                            ),
             dcc.Slider(
                 id='timeframe',
                 min=1,
                 max=60,
                 value=6,
                 marks={
                     1: {'label': '1M'},
                     3: {'label': '3M'},
                     6: {'label': '6M'},
                     12: {'label': '1Y'},
                     24: {'label': '2Y'},
                     36: {'label': '3Y'},
                     48: {'label': '4Y'},
                     60: {'label': '5Y'},
                 },
             ),
             dcc.Loading(id='load-graph', children=[dcc.Graph(id='price_graph')], type='circle'),
             dcc.Loading(id='load-hp', children=[dash_table.DataTable(
                                  id='historic_prices',
                                  style_cell={
                                      'textAlign': 'center',
                                      'whiteSpace': 'normal',
                                      'height': 'auto',
                                      'color': 'white',
                                      'backgroundColor': '#696969',
                                  },
                                  style_header={'backgroundColor': '#000000'},
                                  style_data_conditional=[
                                      {
                                          'if': {
                                              'filter_query': '{{Change from Prior Close}} < {}'.format(0.00),
                                          },
                                          'backgroundColor': '#FF4136',
                                      },
                                      {
                                          'if': {
                                              'filter_query': '{{Change from Prior Close}} > {}'.format(0.00),
                                          },
                                          'backgroundColor': '#3cb371',
                                      },
                                      {
                                          'if': {
                                              'state': 'active'  # 'active' | 'selected'
                                          },
                                          'backgroundColor': '#696969',
                                          'border': '#ffffff',
                                      }
                                  ],
                                  style_as_list_view=True,
                                  page_size=20,
                                  style_table={'height': '400px', 'overflowY': 'auto'}
                )], type='circle')],
             ),
    # Hidden div inside the app that stores the intermediate value
    html.Div(id='Port-Json', style={'display': 'none'})
])


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            return pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            return pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])


@app.callback(Output('Port-Json', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(input_value_1, input_value_2):
    if input_value_1 is not None:
        children = parse_contents(input_value_1, input_value_2)
        return children.to_json(orient='split')


@app.callback(
    [Output(component_id='curr_val_chg', component_property='children'),
     Output(component_id='portfolio_values', component_property='columns'),
     Output(component_id='portfolio_values', component_property='data'),
     Output(component_id='invest_select', component_property='options'),
     Output(component_id='invest_select', component_property='value')],
    [Input(component_id='Port-Json', component_property='children'),
     Input(component_id='Refresh-Portfolio', component_property='n_clicks')]
)
def update_port(input_value_1, input_value_2):
    investments = pd.read_json(input_value_1, orient='split')
    port_tbl_ret = it.port_tbl(investments)
    portfolio = port_tbl_ret[0]
    cur_ret = port_tbl_ret[1]
    return cur_ret,\
           [{"name": i, "id": i} for i in portfolio.keys()], portfolio.to_dict('records'), \
           [{"label": i, "value": j} for i, j in zip(investments['Stock/ETF Ticker Short Name'],
                                                     investments['Ticker'])], \
           investments['Ticker'][0]


@app.callback(
    [Output(component_id='daily_highlights', component_property='columns'),
     Output(component_id='daily_highlights', component_property='data')],
    [Input(component_id='invest_select', component_property='value')]
)
def update_hl(input_value):
    sel = yf.Ticker(input_value)
    hl = it.highlights(sel)
    return [{"name": i, "id": i} for i in hl.keys()], [hl]


@app.callback(
    Output(component_id='price_graph', component_property='figure'),
    [Input(component_id='invest_select', component_property='value'),
     Input(component_id='graph_type', component_property='value'),
     Input(component_id='timeframe', component_property='value')]
)
def update_plot(input_value_1, input_value_2, input_value_3):
    sel = yf.Ticker(input_value_1)
    hist = sel.history(start=datetime.now() - relativedelta(months=input_value_3), end=datetime.now()).reset_index()

    if input_value_2 == 'Candle':
        return ip.candle_plt(hist)

    return ip.lin_plt(hist)


@app.callback(
    [Output(component_id='historic_prices', component_property='columns'),
     Output(component_id='historic_prices', component_property='data')],
    [Input(component_id='invest_select', component_property='value'),
     Input(component_id='timeframe', component_property='value')]
)
def update_hist(input_value_1, input_value_2):
    sel = yf.Ticker(input_value_1)
    hist = sel.history(start=datetime.now() - relativedelta(months=input_value_2), end=datetime.now()).reset_index()
    sel_hist_df = it.his_tbl(hist)
    return [{"name": i, "id": i} for i in sel_hist_df.columns], sel_hist_df.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=False, use_reloader=False)
