# set up
import dash
from dash import dash_table
from dash import dcc
from dash import html 
from dash.dependencies import Input, Output 

import requests 
import plotly.graph_objects as go
import pandas as pd
import datetime
import numpy as np

from tm_stats.elo import compute_historical_player_ratings, compute_historical_corp_ratings,\
                         make_plotly_player_ts_ratings_plot, make_plotly_corp_ts_ratings_plot

# data
df = pd.read_csv('https://raw.githubusercontent.com/AnthonyRentsch/terraforming-mars-stats/main/terraforming-mars-stats.csv')

# pre-computed fields
## future step - figure out how to default to these and then update if someone selects a different scoring function
players_to_display = ['Ben','Ezra','Matt','Pat','Tony']
corps_to_display = set(df[df.corporation_origin=='Base'].corporation.unique()) - set(['Beginner'])
most_recent_game = max(df.date)

player_ratings_df = compute_historical_player_ratings(df, score_fun='linear')
corp_ratings_df = compute_historical_corp_ratings(df, score_fun='linear')

most_recent_player_ratings_df = player_ratings_df[(player_ratings_df.player.isin(players_to_display)) & (player_ratings_df.date == max(player_ratings_df.date))][['player','rating']].sort_values(by='rating', ascending=False)
most_recent_player_ratings_df['rating'] = np.round(most_recent_player_ratings_df['rating'].astype(float), decimals = 0)

most_recent_corp_ratings_df = corp_ratings_df[(corp_ratings_df.corporation.isin(corps_to_display)) & (corp_ratings_df.date == max(corp_ratings_df.date))][['corporation','rating']].sort_values(by='rating', ascending=False)
most_recent_corp_ratings_df['rating'] = np.round(most_recent_corp_ratings_df['rating'].astype(float), decimals = 0)


# app
app = dash.Dash() 
server = app.server

app.layout = html.Div(
    [ 
        html.H1(
            'Terraforming Mars Statistics',
            style = {'text-align' : 'center'}
        ),
        dcc.Tabs(id="app-tabs", value='summary-tab', children=[
            dcc.Tab(label='Summary', value='summary-tab'),
            dcc.Tab(label='Individual Player Statistics', value='individual-player-tab'),
            dcc.Tab(label='Player ELO', value='player-elo-tab'),
            dcc.Tab(label='Corporation ELO', value='corporation-elo-tab')
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
            html.H3(f'Most recent game: {most_recent_game}'),
            html.Br(),
            html.H3('Player Win Rates'),
            dash_table.DataTable(
                id='player-win-rates-table',
                columns=[{"name": i, "id": i} for i in player_win_rates_df.columns],
                data=player_win_rates_df[player_win_rates_df.player.isin(players_to_display)].to_dict('records'),

                style_header={
                    'backgroundColor': 'rgb(30, 30, 30)',
                    'color': 'white'
                },
                style_data={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white'
                }
            )
        ])
    elif tab == 'player-elo-tab':
        player_ratings_plot = make_plotly_player_ts_ratings_plot(player_ratings_df)
        return html.Div([
            html.H2('Player Ratings'),
            html.Br(),
            html.H4(f'Updated ratings (as of {most_recent_game})'),
            dash_table.DataTable(
                id='player-ratings-table',
                columns=[{"name": i, "id": i} for i in most_recent_player_ratings_df.columns],
                data=most_recent_player_ratings_df.to_dict('records'),

                style_header={
                    'backgroundColor': 'rgb(30, 30, 30)',
                    'color': 'white'
                },
                style_data={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white'
                }
            ),
            html.Br(),
            dcc.Graph(id= 'player-rating-ts-fig', figure=player_ratings_plot)
        ])
    elif tab == 'corporation-elo-tab':
        corp_ratings_plot = make_plotly_corp_ts_ratings_plot(corp_ratings_df, df)
        return html.Div([
            html.H2('Corporation Ratings'),
            html.Br(),
            html.H4(f'Updated ratings (as of {most_recent_game})'),
            dash_table.DataTable(
                id='corp-ratings-table',
                columns=[{"name": i, "id": i} for i in most_recent_corp_ratings_df.columns],
                data=most_recent_corp_ratings_df.to_dict('records'),

                style_header={
                    'backgroundColor': 'rgb(30, 30, 30)',
                    'color': 'white'
                },
                style_data={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white'
                }
            ),
            html.Br(),
            dcc.Graph(id= 'corp-rating-ts-fig', figure=corp_ratings_plot)
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