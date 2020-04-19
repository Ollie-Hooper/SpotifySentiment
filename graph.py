from datetime import datetime

import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd

from functions import get_audio_features

country_meta = pd.read_csv('data/country_meta.csv')


def get_graph_colours():
    return dict(
        plot='#002b36',  # plot='#181717',  # plot='#5c7791',
        bg='#002b36',  # bg='#181717',  # bg='#2b3e50',
        text='#fff',  # text='#1DB954',
    )


def default_graph_layout():
    graph_colours = get_graph_colours()
    return dict(
        margin=dict(l=20, r=20, t=10, b=10),
        plot_bgcolor=graph_colours['plot'],
        paper_bgcolor=graph_colours['bg'],
        font=dict(
            color=graph_colours['text']
        ),
        xaxis=dict(
            showgrid=False
        ),
        yaxis=dict(
            showgrid=False
        ),
        uirevision='true',
        polar=dict(
            bgcolor=graph_colours['bg'],
            radialaxis=dict(
                visible=False,
                range=[0, 1],
                showgrid=False,
            ),
            angularaxis=dict(
                visible=True,
                showgrid=False,
                showline=False,
            )
        )
    )


def get_country_features_ts(df, country='GBR'):
    features = get_audio_features()
    chart_df = df[df['iso3'] == country]
    chart_df['date'] = chart_df['date'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y').strftime('%Y-%m-%d'))
    chart_df = chart_df.set_index('date')
    chart_df = chart_df[[f"s_{f}" for f in features]]
    fig = dict(
        data=[
            go.Scatter(
                x=chart_df.index,
                y=chart_df[f"s_{f}"],
                mode='lines',
                name=v[0],
                line=dict(color=v[1]),
            ) for f, v in features.items()
        ],
        layout=dict(
            **default_graph_layout(),
            legend=dict(
                orientation='h'
            )
        )
    )
    return fig


def get_country_features_dist(df, country='GBR'):
    features = get_audio_features()
    del features['instrumentalness']
    features_list = list(features.keys())
    features_list.reverse()
    features = {k: features[k] for k in features_list}
    chart_df = df[df['iso3'] == country]
    fig = ff.create_distplot([chart_df[f] for f in features],
                             group_labels=[v[0] for v in features.values()], colors=[v[1] for v in features.values()],
                             histnorm='probability', show_hist=False,
                             show_rug=False)
    fig.update_layout(**default_graph_layout())
    fig.update_layout(
        xaxis=dict(range=[0, 1], showline=True),
        yaxis=dict(showline=True),
        showlegend=False,
    )
    return fig


def get_country_features_barchart(df, country='GBR'):
    features = get_audio_features()
    chart_df = df[df['iso3'] == country]
    series = chart_df[[f for f in features]].mean() / df[['country', *[f for f in features]]].groupby(
        'country').mean().max()
    fig = dict(
        data=[
            go.Barpolar(
                r=[series.loc[f] for f in features],
                theta=[v[0] for v in features.values()],
                width=1,
                marker_color=[v[1] for v in features.values()],
            ),
        ],
        layout={
            **default_graph_layout(),
            'margin': dict(l=90, r=90),
        }
    )
    return fig


def get_map_figure(df=None, feature='valence', standardised=True):
    if standardised and feature:
        feature = 's_' + feature

    map_df = df[['iso3', 'name', feature]]

    data = get_map_data(map_df, feature)
    layout = get_map_layout()

    fig = dict(
        data=data,
        layout=layout,
    )

    return fig


def get_map_data(df, feature):
    data = [
        go.Choropleth(
            locations=df['iso3'],
            z=df[feature],
            text=df['name'],
            showscale=False,
            colorscale=['red', '#333', 'green'],
            zmid=0,
            uirevision='true',
            hoverinfo='z+text',
        )
    ]
    return data


def get_map_layout():
    layout = dict(
        **default_graph_layout()
    )

    layout.update(dict(
        margin=dict(l=0, r=0, t=0, b=0),

        plot_bgcolor='#21444a',
        paper_bgcolor='#21444a',
        geo=dict(
            showframe=False,
            showcoastlines=True,
            showlakes=True,
            lakecolor='#002b36',
            showocean=True,
            oceancolor='#002b36',
            showland=True,
            landcolor='#333',
            showcountries=True,
            bgcolor='#002b36',
            projection=dict(
                scale=1.1
            )
        ),
    ))
    return layout
