from datetime import datetime

import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd

country_meta = pd.read_csv('data/country_meta.csv')


def get_graph_colours():
    return dict(
        plot='#191414',  # plot='#181717',  # plot='#5c7791',
        bg='#191414',  # bg='#181717',  # bg='#2b3e50',
        text='#1DB954',
    )


def default_graph_layout():
    graph_colours = get_graph_colours()
    return dict(
        # margin=dict(l=20, r=20, t=0, b=30),
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
        uirevision='true'
    )


def get_country_features_ts(df, country='GBR'):
    feature_colors = {
        'danceability': 'purple', 'energy': 'green', 'mode': 'red',
        'speechiness': 'green', 'acousticness': 'green',  # 'instrumentalness': 'green',
        'liveness': 'green', 'valence': 'yellow'
    }
    chart_df = df[df['iso3'] == country]
    chart_df['date'] = chart_df['date'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y').strftime('%Y-%m-%d'))
    chart_df = chart_df.set_index('date')
    chart_df = chart_df[[f"s_{f}" for f in feature_colors]]
    fig = dict(
        data=[
            go.Scatter(
                x=chart_df.index,
                y=chart_df[f"s_{f}"],
                mode='lines',
                name=f,
            ) for f in feature_colors
        ],
        layout={
            **default_graph_layout(),
        }
    )
    return fig


def get_country_features_dist(df, country='GBR'):
    feature_colors = {
        'danceability': 'purple', 'energy': 'green', 'mode': 'red',
        'speechiness': 'green', 'acousticness': 'green',  # 'instrumentalness': 'green',
        'liveness': 'green', 'valence': 'yellow'
    }
    chart_df = df[df['iso3'] == country]
    fig = ff.create_distplot([chart_df[f] for f in feature_colors],
                             group_labels=[f for f in feature_colors], histnorm='probability', show_hist=False,
                             show_rug=False)
    fig.update_layout(**default_graph_layout())
    fig.update_layout(xaxis=dict(range=[0, 1]), yaxis=dict(showline=True, mirror=True))
    return fig


def get_country_features_barchart(df, country='GBR'):
    feature_colors = {
        'danceability': 'purple', 'energy': 'green', 'mode': 'red',
        'speechiness': 'green', 'acousticness': 'green',  # 'instrumentalness': 'green',
        'liveness': 'green', 'valence': 'yellow'
    }
    chart_df = df[df['iso3'] == country]
    series = chart_df[[f for f in feature_colors]].mean() - df[df['country'] == 'global'][
        [f for f in feature_colors]].mean()
    fig = dict(
        data=[
            {
                'x': [feature],
                'y': [val],
                'text': [feature],
                'type': 'bar',
            } for feature, val in series.iteritems()
        ],
        layout={
            **default_graph_layout(),
            'showlegend': False
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
        geo=dict(
            showframe=False,
            showcoastlines=True,
            showlakes=True,
            lakecolor='#111',
            showocean=True,
            oceancolor='#111',
            showland=True,
            landcolor='#333',
            showcountries=True,
            bgcolor='#111',
            projection=dict(
                scale=1.1
            )
        ),
    ))
    return layout
