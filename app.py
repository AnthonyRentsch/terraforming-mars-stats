# set up
import dash
from dash import dash_table
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
        dcc.Tabs(id="app-tabs", value='app-tabs', children=[
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
    if tab == 'summary-tab':
        player_win_rates_df = get_player_win_rates_table(df)
        return html.Div([
            html.H3('Player Win Rates'),
            dash_table.DataTable(
                id='player-win-rates-table',
                columns=[{"name": i, "id": i} for i in player_win_rates_df.columns],
                data=player_win_rates_df.to_dict('records'),
            )
        ])
    else:
        return html.Div([
            html.H3('Coming soon...')
        ])

def get_player_win_rates_table(df):
    return df.groupby('player').\
    agg(wins = ('is_winner','sum'), games = ('is_winner', 'count'), win_rate = ('is_winner','mean')).\
    sort_values(by='win_rate', ascending=False).reset_index()

if __name__ == '__main__': 
    app.run_server(port=8000, host='127.0.0.1', debug=True)