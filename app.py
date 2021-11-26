# set up
import dash
import dash_table
from dash import dcc
from dash import html 
from dash.dependencies import Input, Output 

import requests 
import plotly.graph_objects as go
import pandas as pd

# data
df = pd.read_csv('https://raw.githubusercontent.com/AnthonyRentsch/terraforming-mars-stats/main/terraforming-mars-stats.csv')

# app
app = dash.Dash() 
server = app.server

app.layout = html.Div(
    [ 
        html.H1(
            'Terraforming Mars Statistics',
            style = {'text-align' : 'center'}
        ),
        dcc.Tabs(id="app-tabs", value='tab-1-example-graph', children=[
            dcc.Tab(label='Summary', value='summary-tab'),
            dcc.Tab(label='Individual Player Statistics', value='individual-player-tab'),
            dcc.Tab(label='Player ELO', value='player-elo-tab'),
            dcc.Tab(label='Corporation ELO', value='corporaion-elo-tab')
    ]),
        html.Div(id='tab-content')
    ]
)

@app.callback(Output('tab-content', 'children'),
              Input('app-tabs', 'value'))
def render_content(tab):
    if tab == 'Summary':
        return html.Div([
            html.H3('Player Win Rates'),
            dcc.Graph(
                id='graph-1-tabs',
                figure={
                    'data': [{
                        'x': [1, 2, 3],
                        'y': [3, 1, 2],
                        'type': 'bar'
                    }]
                }
            )
        ])
    return 

if __name__ == '__main__': 
    app.run_server(port=8000, host='127.0.0.1', debug=True)