# set up
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

import requests
import pandas as pd
import datetime
import numpy as np

import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots

from tm_stats.elo import (
    compute_historical_player_ratings,
    compute_historical_corp_ratings,
    make_plotly_player_ts_ratings_plot,
    make_plotly_corp_ts_ratings_plot,
)

# data
df = pd.read_csv(
    "https://raw.githubusercontent.com/AnthonyRentsch/terraforming-mars-stats/main/terraforming-mars-stats.csv"
)
df["corporation_origin"] = df["corporation_origin"].str.strip()

# pre-computed fields
most_recent_game_date = max(df.date)
most_recent_game_df = df[df.date == max(df.date)]

# app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div(
    [
        html.H1("Terraforming Mars Statistics"),
        dcc.Tabs(
            id="app-tabs",
            value="most-recent-game-tab",
            children=[
                dcc.Tab(label="Most Recent Game", value="most-recent-game-tab"),
                dcc.Tab(label="Player Statistics", value="player-stats-tab"),
                dcc.Tab(label="Player ELO", value="player-elo-tab"),
                dcc.Tab(label="Corporation ELO", value="corporation-elo-tab"),
                dcc.Tab(label="View Raw Data", value="raw-data-tab"),
            ],
        ),
        html.Div(id="tab-content"),
        html.Br(),
        html.Div(
            [
                dcc.Markdown(
                    "Dashboard built by Anthony Rentsch. To view the source code or download the raw data, visit my [terraforming-mars-stats Github repository](https://github.com/AnthonyRentsch/terraforming-mars-stats)",
                    className="footer",
                )
            ]
        ),
    ]
)


@app.callback(Output("tab-content", "children"), Input("app-tabs", "value"))
def render_content(tab):
    if tab == "most-recent-game-tab":
        return html.Div(
            [
                html.H3(
                    f"{most_recent_game_date}", style={"text-decoration": "underline"}
                ),
                dcc.Markdown(
                    f"""**Board**: {most_recent_game_df['board'][0]}
            \n**Expansions**: {", ".join([col for col in ['prelude','venus','colonies','turmoil','bgg'] if most_recent_game_df[col].sum() == most_recent_game_df.shape[0]])}
            \n**Award 1**: {most_recent_game_df['award_1_name'][0]} (funder = {most_recent_game_df['award_1_funder'][0]})
            \n**Award 2**: {most_recent_game_df['award_2_name'][0]} (funder = {most_recent_game_df['award_2_funder'][0]})
            \n**Award 3**: {most_recent_game_df['award_3_name'][0]} (funder = {most_recent_game_df['award_3_funder'][0]})
            \n**Milestone 1**: {most_recent_game_df['milestone_1_name'][0]}
            \n**Milestone 2**: {most_recent_game_df['milestone_2_name'][0]}
            \n**Milestone 3**: {most_recent_game_df['milestone_3_name'][0]}""",
                    className="p",
                ),
                dash_table.DataTable(
                    id="most-recent-game-table",
                    columns=[
                        {"name": i, "id": i}
                        for i in most_recent_game_df[
                            [
                                "player",
                                "corporation",
                                "terraform_rating",
                                "award_1_points",
                                "award_2_points",
                                "award_3_points",
                                "milestone_1_points",
                                "milestone_2_points",
                                "milestone_3_points",
                                "num_greeneries",
                                "num_cities",
                                "num_colonies",
                                "num_greenery_adjacencies",
                                "card_points",
                                "total_points",
                            ]
                        ]
                        .set_index("player")
                        .T.reset_index()
                        .columns
                    ],
                    data=most_recent_game_df[
                        [
                            "player",
                            "corporation",
                            "terraform_rating",
                            "award_1_points",
                            "award_2_points",
                            "award_3_points",
                            "milestone_1_points",
                            "milestone_2_points",
                            "milestone_3_points",
                            "num_greeneries",
                            "num_cities",
                            "num_colonies",
                            "num_greenery_adjacencies",
                            "card_points",
                            "total_points",
                        ]
                    ]
                    .set_index("player")
                    .T.reset_index()
                    .to_dict("records"),
                    style_header={
                        "backgroundColor": "rgb(30, 30, 30)",
                        "color": "white",
                    },
                    style_data={"backgroundColor": "rgb(50, 50, 50)", "color": "white"},
                    style_table={
                        "width": "50%",
                        "margin-left": "auto",
                        "margin-right": "auto",
                    },
                    include_headers_on_copy_paste=True,
                ),
            ]
        )
    elif tab == "player-stats-tab":
        return html.Div(
            [
                html.H2("Overall Player Win Rates"),
                html.H4("Players Included (in output)"),
                dcc.Dropdown(
                    id="player-win-rate-players-included-dropdown",
                    options=[
                        {"label": name, "value": name}
                        for name in sorted(df.player.unique())
                    ],
                    multi=True,
                    value=["Ben", "Ezra", "Matt", "Pat", "Tony"],
                ),
                html.Br(),
                html.Div(id="player-win-rate-div"),
                html.Br(),
                html.H4("Choose a player to learn more about"),
                dcc.Dropdown(
                    id="player-drill-down-dropdown",
                    options=[
                        {"label": name, "value": name}
                        for name in sorted(df.player.unique())
                    ],
                    value="Tony",
                ),
                html.Div(id="player-drill-down-div"),
                html.Div(id="player-points-on-cards-div"),
            ]
        )

    elif tab == "player-elo-tab":
        return html.Div(
            [
                html.H4("Game Type"),
                dcc.Dropdown(
                    id="player-elo-options-dropdown",
                    options=[
                        {"label": "All games", "value": "all"},
                        {"label": "Only two player games", "value": "two-player"},
                        {
                            "label": "Only non-two player games",
                            "value": "non-two-player",
                        },
                    ],
                    value="all",
                ),
                html.H4("ELO Scoring Function"),
                dcc.Dropdown(
                    id="player-elo-score-function-dropdown",
                    options=[
                        {"label": "Linear", "value": "linear"},
                        {"label": "Exponential", "value": "exp"},
                    ],
                    value="linear",
                ),
                html.H4("Players Included (in output)"),
                dcc.Dropdown(
                    id="player-elo-players-included-dropdown",
                    options=[
                        {"label": name, "value": name}
                        for name in sorted(df.player.unique())
                    ],
                    multi=True,
                    value=["Ben", "Ezra", "Matt", "Pat", "Tony"],
                ),
                html.Div(id="player-elo-div"),
            ]
        )
    elif tab == "corporation-elo-tab":
        return html.Div(
            [
                html.H4("Expansions Included (in output)"),
                dcc.Dropdown(
                    id="corp-elo-expansion-included-dropdown",
                    options=[
                        {"label": corp_origin, "value": corp_origin}
                        for corp_origin in sorted(df.corporation_origin.unique())
                    ],
                    multi=True,
                    value=["Base"],
                ),
                html.H4("ELO Scoring Function"),
                dcc.Dropdown(
                    id="corp-elo-score-function-dropdown",
                    options=[
                        {"label": "Linear", "value": "linear"},
                        {"label": "Exponential", "value": "exp"},
                    ],
                    value="linear",
                ),
                html.Div(id="corp-elo-div"),
            ]
        )
    elif tab == "raw-data-tab":
        return html.Div(
            [
                html.Br(),
                dash_table.DataTable(
                    id="raw-data-table",
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict("records"),
                    style_header={
                        "backgroundColor": "rgb(30, 30, 30)",
                        "color": "white",
                    },
                    style_data={"backgroundColor": "rgb(50, 50, 50)", "color": "white"},
                    style_table={
                        "overflowY": "scroll",
                        "overflowX": "scroll",
                        "minWidth": "100%",
                    },
                    filter_action="native",
                    page_size=50,
                    fixed_columns={"headers": True, "data": 3},
                ),
            ]
        )
    else:
        return html.Div([html.H3("Coming soon...")])


#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################

### PLAYER STATISTICS ###
@app.callback(
    Output("player-win-rate-div", "children"),
    Input("player-win-rate-players-included-dropdown", "value"),
)
def get_player_win_rates_table(players_to_include):
    player_win_rates_df_ = (
        df.groupby("player")
        .agg(
            wins=("is_winner", "sum"),
            games=("is_winner", "count"),
            win_rate=("is_winner", "mean"),
        )
        .sort_values(by="win_rate", ascending=False)
        .reset_index()
    )

    player_win_rates_df = player_win_rates_df_[
        player_win_rates_df_.player.isin(players_to_include)
    ]

    return html.Div(
        [
            dash_table.DataTable(
                id="player-win-rates-table",
                columns=[{"name": i, "id": i} for i in player_win_rates_df.columns],
                data=player_win_rates_df.to_dict("records"),
                style_header={"backgroundColor": "rgb(30, 30, 30)", "color": "white"},
                style_data={"backgroundColor": "rgb(50, 50, 50)", "color": "white"},
                style_table={
                    "width": "50%",
                    "margin-left": "auto",
                    "margin-right": "auto",
                },
                include_headers_on_copy_paste=True,
            )
        ]
    )


@app.callback(
    Output("player-drill-down-div", "children"),
    Input("player-drill-down-dropdown", "value"),
)
def make_player_most_recent_win_div(player):
    player_df = df[df.player == player]

    if player_df["is_winner"].sum() > 0:
        player_most_recent_win_game_id = (
            player_df[player_df["is_winner"] == 1]
            .sort_values(by="date", ascending=False)
            .head(1)["game_id"]
            .values[0]
        )
        player_most_recent_win_df = df[df.game_id == player_most_recent_win_game_id]

        return html.Div(
            [
                html.H3(
                    f'Most recent win: {player_most_recent_win_df["date"].values[0]}',
                    style={"text-decoration": "underline"},
                ),
                dcc.Markdown(
                    f"""**Board**: {player_most_recent_win_df['board'].values[0]}
            \n**Expansions**: {", ".join([col for col in ['prelude','venus','colonies','turmoil','bgg'] if player_most_recent_win_df[col].sum() == player_most_recent_win_df.shape[0]])}
            \n**Award 1**: {player_most_recent_win_df['award_1_name'].values[0]} (funder = {player_most_recent_win_df['award_1_funder'].values[0]})
            \n**Award 2**: {player_most_recent_win_df['award_2_name'].values[0]} (funder = {player_most_recent_win_df['award_2_funder'].values[0]})
            \n**Award 3**: {player_most_recent_win_df['award_3_name'].values[0]} (funder = {player_most_recent_win_df['award_3_funder'].values[0]})
            \n**Milestone 1**: {player_most_recent_win_df['milestone_1_name'].values[0]}
            \n**Milestone 2**: {player_most_recent_win_df['milestone_2_name'].values[0]}
            \n**Milestone 3**: {player_most_recent_win_df['milestone_3_name'].values[0]}""",
                    className="p",
                ),
                dash_table.DataTable(
                    id="most-recent-player-win-table",
                    columns=[
                        {"name": i, "id": i}
                        for i in player_most_recent_win_df[
                            [
                                "player",
                                "corporation",
                                "terraform_rating",
                                "award_1_points",
                                "award_2_points",
                                "award_3_points",
                                "milestone_1_points",
                                "milestone_2_points",
                                "milestone_3_points",
                                "num_greeneries",
                                "num_cities",
                                "num_colonies",
                                "num_greenery_adjacencies",
                                "card_points",
                                "total_points",
                            ]
                        ]
                        .set_index("player")
                        .T.reset_index()
                        .columns
                    ],
                    data=player_most_recent_win_df[
                        [
                            "player",
                            "corporation",
                            "terraform_rating",
                            "award_1_points",
                            "award_2_points",
                            "award_3_points",
                            "milestone_1_points",
                            "milestone_2_points",
                            "milestone_3_points",
                            "num_greeneries",
                            "num_cities",
                            "num_colonies",
                            "num_greenery_adjacencies",
                            "card_points",
                            "total_points",
                        ]
                    ]
                    .set_index("player")
                    .T.reset_index()
                    .to_dict("records"),
                    style_header={
                        "backgroundColor": "rgb(30, 30, 30)",
                        "color": "white",
                    },
                    style_data={"backgroundColor": "rgb(50, 50, 50)", "color": "white"},
                    style_table={
                        "width": "50%",
                        "margin-left": "auto",
                        "margin-right": "auto",
                    },
                    include_headers_on_copy_paste=True,
                ),
            ]
        )

    else:
        return html.Div(
            [
                html.H3("No wins yet!", style={"text-decoration": "underline"}),
            ]
        )


@app.callback(
    Output("player-points-on-cards-div", "children"),
    Input("player-drill-down-dropdown", "value"),
)
def make_player_points_on_card_div(player):
    player_df = df[df.player == player]
    fig = make_subplots(
        rows=1,
        cols=4,
        subplot_titles=[f"{i}-player" for i in sorted(df.num_players.unique())],
    )

    for i, n_players in enumerate(sorted(df.num_players.unique())):
        player_df_num_players = player_df[player_df.num_players == n_players]
        other_player_df_num_players = df[
            (df.player != player) & (df.num_players == n_players)
        ]

        hist_data = [
            player_df_num_players.card_points,
            other_player_df_num_players.card_points,
        ]

        group_labels = [player, "Field"]
        colors = ["blue", "grey"]

        data_ = ff.create_distplot(hist_data, group_labels, colors=colors, bin_size=5)

        if i > 0:
            fig.add_trace(
                go.Histogram(data_["data"][0], marker_color="blue", showlegend=False),
                row=1,
                col=i + 1,
            )
            fig.add_trace(
                go.Histogram(data_["data"][1], marker_color="grey", showlegend=False),
                row=1,
                col=i + 1,
            )
        else:
            fig.add_trace(
                go.Histogram(data_["data"][0], marker_color="blue"), row=1, col=i + 1
            )
            fig.add_trace(
                go.Histogram(data_["data"][1], marker_color="grey"), row=1, col=i + 1
            )

    #     fig.add_trace(go.Scatter(data_['data'][2], line=dict(color='blue', width=0.5)),
    #                   row=1, col=i+1)
    #     fig.add_trace(go.Scatter(data_['data'][3], line=dict(color='grey', width=0.5)),
    #                   row=1, col=i+1)

    fig.update_layout(
        title_text=f"Points from Cards: {player} vs. Field",
        title_x=0.5,
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_yaxes(showticklabels=False)
    return html.Div([dcc.Graph(id="player-points-on-card-fig", figure=fig)])


### PLAYER ELO ###
@app.callback(
    Output("player-elo-div", "children"),
    Input("player-elo-options-dropdown", "value"),
    Input("player-elo-score-function-dropdown", "value"),
    Input("player-elo-players-included-dropdown", "value"),
)
def make_player_elo_div(num_player_category, score_fun, included_players):

    if num_player_category == "all":
        player_ratings_df = compute_historical_player_ratings(
            df=df, score_fun=score_fun
        )
    elif num_player_category == "two-player":
        player_ratings_df = compute_historical_player_ratings(
            df=df[df.num_players == 2], score_fun=score_fun
        )
    elif num_player_category == "non-two-player":
        player_ratings_df = compute_historical_player_ratings(
            df=df[df.num_players != 2], score_fun=score_fun
        )

    player_ratings_plot = make_plotly_player_ts_ratings_plot(
        player_ratings_df[player_ratings_df.player.isin(included_players)]
    )

    most_recent_player_ratings_df = player_ratings_df[
        (player_ratings_df.player.isin(included_players))
        & (player_ratings_df.date == max(player_ratings_df.date))
    ][["player", "rating"]].sort_values(by="rating", ascending=False)
    most_recent_player_ratings_df["rating"] = np.round(
        most_recent_player_ratings_df["rating"].astype(float), decimals=0
    )

    return html.Div(
        [
            html.H3(f"Current ratings (as of {most_recent_game_date})"),
            dash_table.DataTable(
                id="player-ratings-table",
                columns=[
                    {"name": i, "id": i} for i in most_recent_player_ratings_df.columns
                ],
                data=most_recent_player_ratings_df.to_dict("records"),
                style_header={"backgroundColor": "rgb(30, 30, 30)", "color": "white"},
                style_data={"backgroundColor": "rgb(50, 50, 50)", "color": "white"},
                style_table={
                    "width": "50%",
                    "margin-left": "auto",
                    "margin-right": "auto",
                },
                include_headers_on_copy_paste=True,
            ),
            html.Br(),
            dcc.Graph(id="player-rating-ts-fig", figure=player_ratings_plot),
        ]
    )


### CORP ELO ###
@app.callback(
    Output("corp-elo-div", "children"),
    Input("corp-elo-expansion-included-dropdown", "value"),
    Input("corp-elo-score-function-dropdown", "value"),
)
def make_corp_elo_div(corps_to_display, score_fun):
    corp_ratings_df = compute_historical_corp_ratings(df=df, score_fun=score_fun)
    corp_ratings_plot = make_plotly_corp_ts_ratings_plot(
        corp_ratings_df=corp_ratings_df[
            corp_ratings_df.corporation_origin.isin(corps_to_display)
        ],
        df=df,
    )

    most_recent_corp_ratings_df = corp_ratings_df[
        (corp_ratings_df.corporation_origin.isin(corps_to_display))
        & (corp_ratings_df.date == max(corp_ratings_df.date))
    ][["corporation", "corporation_origin", "rating"]].sort_values(
        by="rating", ascending=False
    )
    most_recent_corp_ratings_df["rating"] = np.round(
        most_recent_corp_ratings_df["rating"].astype(float), decimals=0
    )

    return html.Div(
        [
            html.H3(f"Current ratings (as of {most_recent_game_date})"),
            dash_table.DataTable(
                id="corp-ratings-table",
                columns=[
                    {"name": i, "id": i} for i in most_recent_corp_ratings_df.columns
                ],
                data=most_recent_corp_ratings_df.to_dict("records"),
                style_header={"backgroundColor": "rgb(30, 30, 30)", "color": "white"},
                style_data={"backgroundColor": "rgb(50, 50, 50)", "color": "white"},
                style_table={
                    "width": "50%",
                    "margin-left": "auto",
                    "margin-right": "auto",
                },
                include_headers_on_copy_paste=True,
            ),
            html.Br(),
            dcc.Graph(id="corp-rating-ts-fig", figure=corp_ratings_plot),
        ]
    )


if __name__ == "__main__":
    app.run_server(port=8000, host="127.0.0.1", debug=True)
