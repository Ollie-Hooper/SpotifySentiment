import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from functions import get_audio_features
from graph import get_map_figure, get_country_features_dist, get_country_features_ts, \
    get_country_features_barchart

graph_config = {
    'displayModeBar': False
}


def get_layout(df):
    layout = html.Div([
        dbc.Row([
            dbc.Col([
                dbc.NavbarSimple(
                    [
                        dbc.Select(id='feature-dropdown',
                                   options=[{'label': v[0], 'value': k} for k, v in get_audio_features().items()],
                                   value='valence'),
                        dbc.NavItem(dbc.NavLink('back', href=''))
                    ],
                    brand='Spotify Sentiment'
                )
            ])
        ], no_gutters=True),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H1(id='country', children='United Kingdom'),
                        html.P(id='country-description', className='lead'),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id='country-barchart', figure=get_country_features_barchart(df),
                                          config=graph_config)
                            ], width=6),
                            dbc.Col([
                                dcc.Graph(id='country-dist', figure=get_country_features_dist(df), config=graph_config)
                            ], width=6),
                        ]),
                        html.Br(),
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id='country-ts', figure=get_country_features_ts(df), config=graph_config)
                            ])
                        ])
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='map', figure=get_map_figure(df), config=graph_config),
                        dbc.Row([
                            dbc.Col([
                                dcc.Slider(
                                    id='map-slider',
                                    min=0,
                                    max=len(df.date.unique()) - 1,
                                    value=len(df.date.unique()) - 1,
                                    marks={
                                        i: df.date.unique()[i] for i in range(len(df.date.unique()) - 1, -1, -16)
                                    },
                                    included=False,
                                    updatemode='drag',
                                )
                            ], width=10),
                            dbc.Col([
                                html.H3(id='map-date')
                            ], width=2)
                        ]),
                    ])
                ]),
                dbc.Card([
                    dbc.CardBody([
                    ])
                ]),
            ], width=6),
        ], no_gutters=True),
    ])

    return layout
