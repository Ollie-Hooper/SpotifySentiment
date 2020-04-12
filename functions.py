import time
from functools import wraps

import pandas as pd

from database.tools import Database


def time_method(func):
    @wraps(func)
    def timed(*args, **kw):
        ts = time.time()
        result = func(*args, **kw)
        te = time.time()

        print("%r took %2.2f seconds to run." % (func.__name__, te - ts))

        return result

    return timed


def get_audio_features():
    return {
        'valence': ['Valence', '#6fdc8c'],
        'mode': ['Mode', '#08bdba'],
        'energy': ['Energy', '#fa4d56'],
        'danceability': ['Danceability', '#8a3ffc'],
        'speechiness': ['Speechiness', '#bae6ff'],
        'acousticness': ['Acousticness', '#007d79'],
        'instrumentalness': ['Instrumentalness', '#fff1f1'],
        'liveness': ['Liveness', '#d12771'],
    }


def load_data(chart, time_frame):
    t_name = f"{chart.replace(' ', '').lower()}_{time_frame[0]}"
    with Database('scores') as db:
        scores_df = db.select(t_name)
    scores_df.reset_index(drop=True, inplace=True)
    scores_df.set_index(['date', 'country'], inplace=True)
    country_meta = pd.read_csv('data/country_meta.csv')
    country_meta.set_index('country', inplace=True)
    scores_df = pd.merge(scores_df, country_meta[['name', 'iso3']], how='outer', left_index=True, right_index=True)
    scores_df.reset_index(inplace=True)
    scores_df['date'] = pd.to_datetime(scores_df['date'])
    scores_df['date'] = scores_df['date'].apply(lambda x: x.strftime('%d/%m/%Y'))
    return scores_df


def country_geo_json(countries):
    for i in range(len(countries['features'])):
        countries['features'][i]['id'] = countries['features'][i]['properties']['iso_a3']
    return countries
