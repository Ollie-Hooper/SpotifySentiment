import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from app.functions import load_data, get_country_description
from app.graph import get_map_figure, get_country_features_dist, get_country_features_barchart, get_country_features_ts
from app.layout import get_layout

df = dict(
    top200_w=load_data('Top 200', 'weekly'),
    # top200_d=load_data('Top 200', 'daily'),
    # viral50_w=load_data('Viral 50', 'weekly'),
    # viral50_d=load_data('Viral 50', 'daily')
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
app.title = 'Spotify Sentiment'
app.layout = get_layout(df['top200_w'])
server = app.server


@app.callback(
    [Output('map', 'figure'),
     Output('map-date', 'children')],
    [Input('feature-dropdown', 'value'),
     Input('map-slider', 'value')]
)
def update_map(feature, date_i):
    chart = 'Top 200'
    time_frame = 'weekly'
    date = df['top200_w'].date.unique()[date_i]
    fig = get_map_figure(df[f"{chart.replace(' ', '').lower()}_{time_frame[0]}"][df['top200_w']['date'] == date],
                         feature=feature)
    return fig, date[:-4] + date[-2:]


@app.callback(
    [Output('country', 'children'),
     Output('country-description', 'children'),
     Output('country-ts', 'figure'),
     Output('country-dist', 'figure'),
     Output('country-barchart', 'figure')],
    [Input('map', 'clickData')]
)
def update_country_graphs(click):
    if not click:
        raise PreventUpdate()
    country_name = click['points'][0]['text']
    country_iso3 = click['points'][0]['location']
    return country_name, get_country_description(df['top200_w'], country_iso3), \
           get_country_features_ts(df['top200_w'], country_iso3), \
           get_country_features_dist(df['top200_w'], country_iso3), \
           get_country_features_barchart(df['top200_w'], country_iso3)


if __name__ == '__main__':
    app.run_server()
