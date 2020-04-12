import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from functions import get_audio_features
from graph import get_map_figure, get_country_features_dist, get_country_features_ts, \
    get_country_features_barchart

padding = 20

padding_style = {
    'paddingTop': f'{padding}px',
    'paddingBottom': f'{padding}px',
    'paddingLeft': f'{padding}px',
    'paddingRight': f'{padding}px',
}

graph_config = {
    'displayModeBar': False
}


def get_layout(df):
    layout = html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id='map', figure=get_map_figure(df), config=graph_config, style={**padding_style})
                    ], width=12)
                ], no_gutters=True),
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id='country-ts', figure=get_country_features_ts(df), config=graph_config,
                                  style={**padding_style})
                    ], width=12)
                ], no_gutters=True),
            ], width=6),
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            html.H2(id='country', children='United Kingdom')
                        ])
                    ], width=8),
                    dbc.Col([
                        dbc.Select(id='feature-dropdown',
                                   options=[{'label': v[0], 'value': k} for k, v in get_audio_features().items()],
                                   value='valence')
                    ], width=4),
                ], no_gutters=True),
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id='country-dist', figure=get_country_features_dist(df), config=graph_config,
                                  style={**padding_style})
                    ])
                ], no_gutters=True),
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id='country-barchart', figure=get_country_features_barchart(df), config=graph_config,
                                  style={**padding_style})
                    ])
                ], no_gutters=True),
            ], width=6),
        ], no_gutters=True)
    ])
    return layout
