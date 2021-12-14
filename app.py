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
df['corporation_origin'] = df['corporation_origin'].str.strip()

# pre-computed fields
most_recent_game_date = max(df.date)
most_recent_game_df = df[df.date == max(df.date)]

# app
app = dash.Dash(__name__, suppress_callback_exceptions=True) 
server = app.server

app.layout = html.Div(
    [ 
        html.H1(
            'Terraforming Mars Statistics',
            style = {'text-align' : 'center'}
        ),
        dcc.Tabs(id="app-tabs", value='most-recent-game-tab', children=[
            dcc.Tab(label='Most Recent Game', value='most-recent-game-tab'),
            dcc.Tab(label='Player Statistics', value='player-stats-tab'),
            dcc.Tab(label='Player ELO', value='player-elo-tab'),
            dcc.Tab(label='Corporation ELO', value='corporation-elo-tab')
    ]),
        html.Div(id='tab-content')
    ]
)

@app.callback(Output('tab-content', 'children'),
              Input('app-tabs', 'value'))
def render_content(tab):
    if tab == 'most-recent-game-tab':
        return html.Div([
            html.H3(f'{most_recent_game_date}', style = {
                'text-decoration': 'underline'
            }),
            dcc.Markdown(f'''**Board**: {most_recent_game_df['board'][0]}
            \n**Expansions**: {", ".join([col for col in ['prelude','venus','colonies','turmoil','bgg'] if most_recent_game_df[col].sum() == most_recent_game_df.shape[0]])}
            \n**Award 1**: {most_recent_game_df['award_1_name'][0]} (funder = {most_recent_game_df['award_1_funder'][0]})
            \n**Award 2**: {most_recent_game_df['award_2_name'][0]} (funder = {most_recent_game_df['award_2_funder'][0]})
            \n**Award 3**: {most_recent_game_df['award_3_name'][0]} (funder = {most_recent_game_df['award_3_funder'][0]})
            \n**Milestone 1**: {most_recent_game_df['milestone_1_name'][0]}
            \n**Milestone 2**: {most_recent_game_df['milestone_2_name'][0]}
            \n**Milestone 3**: {most_recent_game_df['milestone_3_name'][0]}'''
            ),
            dash_table.DataTable(
                id='most-recent-game-table',
                columns=[{"name": i, "id":i} for i in most_recent_game_df[['player','corporation','terraform_rating','award_1_points','award_2_points','award_3_points','milestone_1_points','milestone_2_points','milestone_3_points','num_greeneries','num_cities','num_colonies','num_greenery_adjancies','card_points','total_points']].set_index('player').T.reset_index().columns],
                data=most_recent_game_df[['player','corporation','terraform_rating','award_1_points','award_2_points','award_3_points','milestone_1_points','milestone_2_points','milestone_3_points','num_greeneries','num_cities','num_colonies','num_greenery_adjancies','card_points','total_points']].set_index('player').T.reset_index().to_dict('records'),
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
    elif tab == 'player-stats-tab':
        player_win_rates_df = get_player_win_rates_table(df)
        return html.Div([
            html.H3('Player Win Rates'),
            dash_table.DataTable(
                id='player-win-rates-table',
                columns=[{"name": i, "id": i} for i in player_win_rates_df.columns],
                data=player_win_rates_df.to_dict('records'),
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
        return html.Div([
            html.H4('Game Type'),
            dcc.Dropdown(
                id='player-elo-options-dropdown',
                options=[
                    {'label': 'All games', 'value': 'all'},
                    {'label': 'Only two player games', 'value': 'two-player'},
                    {'label': 'Only non-two player games', 'value':'non-two-player'}
                ],
                value='all'
            ),
            html.H4('ELO Scoring Function'),
            dcc.Dropdown(
                id='player-elo-score-function-dropdown',
                options=[
                    {'label': 'Linear', 'value': 'linear'},
                    {'label': 'Exponential', 'value': 'exp'}
                ],
                value='linear'
            ),
            html.H4('Players Included'),
            dcc.Dropdown(
                id='player-elo-players-included-dropdown',
                options=[
                    {'label': name, 'value': name} for name in sorted(df.player.unique())
                ],
                multi=True,
                value=['Ben','Ezra','Matt','Pat','Tony']
            ),
            html.Div(id='player-elo-div')
        ])
    elif tab == 'corporation-elo-tab':
        return html.Div([
            html.H4('Expansions Included'),
            dcc.Dropdown(
                id='corp-elo-expansion-included-dropdown',
                options=[
                    {'label': corp_origin, 'value': corp_origin} for corp_origin in sorted(df.corporation_origin.unique())
                ],
                multi=True,
                value=['Base']
            ),
            html.H4('ELO Scoring Function'),
            dcc.Dropdown(
                id='corp-elo-score-function-dropdown',
                options=[
                    {'label': 'Linear', 'value': 'linear'},
                    {'label': 'Exponential', 'value': 'exp'}
                ],
                value='linear'
            ),
            html.Div(id='corp-elo-div')
        ])
    else:
        return html.Div([
            html.H3('Coming soon...')
        ])

#########################################################################################################
def get_player_win_rates_table(df):
    return df.groupby('player').\
    agg(wins = ('is_winner','sum'), games = ('is_winner', 'count'), win_rate = ('is_winner','mean')).\
    sort_values(by='win_rate', ascending=False).reset_index()

@app.callback(
    Output('player-elo-div', 'children'),
    Input('player-elo-options-dropdown', 'value'),
    Input('player-elo-score-function-dropdown', 'value'),
    Input('player-elo-players-included-dropdown', 'value')
)
def make_player_elo_div(num_player_category, score_fun, included_players):

    if num_player_category == 'all':
        player_ratings_df = compute_historical_player_ratings(df = df, score_fun = score_fun)
    elif num_player_category == 'two-player':
        player_ratings_df = compute_historical_player_ratings(df = df[df.num_players==2], score_fun = score_fun)
    elif num_player_category == 'non-two-player':
        player_ratings_df = compute_historical_player_ratings(df = df[df.num_players!=2], score_fun = score_fun)
    
    player_ratings_plot = make_plotly_player_ts_ratings_plot(player_ratings_df[player_ratings_df.player.isin(included_players)])

    most_recent_player_ratings_df = player_ratings_df[(player_ratings_df.player.isin(included_players)) & (player_ratings_df.date == max(player_ratings_df.date))][['player','rating']].sort_values(by='rating', ascending=False)
    most_recent_player_ratings_df['rating'] = np.round(most_recent_player_ratings_df['rating'].astype(float), decimals = 0)
    
    return html.Div([
        html.H4(f'Updated ratings (as of {most_recent_game_date})'),
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
        dcc.Graph(id='player-rating-ts-fig', figure=player_ratings_plot)
    ])

@app.callback(
    Output('corp-elo-div', 'children'),
    Input('corp-elo-expansion-included-dropdown', 'value'),
    Input('corp-elo-score-function-dropdown', 'value'),
)
def make_corp_elo_div(corps_to_display, score_fun):
    corp_ratings_df = compute_historical_corp_ratings(df = df
                                                      , score_fun=score_fun)
    corp_ratings_plot = make_plotly_corp_ts_ratings_plot(corp_ratings_df = corp_ratings_df[corp_ratings_df.corporation_origin.isin(corps_to_display)]
                                                         , df = df)

    most_recent_corp_ratings_df = corp_ratings_df[(corp_ratings_df.corporation_origin.isin(corps_to_display)) & (corp_ratings_df.date == max(corp_ratings_df.date))][['corporation','corporation_origin','rating']].sort_values(by='rating', ascending=False)
    most_recent_corp_ratings_df['rating'] = np.round(most_recent_corp_ratings_df['rating'].astype(float), decimals = 0)

    return html.Div([
        html.H4(f'Updated ratings (as of {most_recent_game_date})'),
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


if __name__ == '__main__': 
    app.run_server(port=8000, host='127.0.0.1', debug=True)