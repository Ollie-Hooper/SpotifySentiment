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
    scores_df = scores_df.sort_values(by='date')
    scores_df['date'] = scores_df['date'].apply(lambda x: x.strftime('%d/%m/%Y'))
    return scores_df


def country_geo_json(countries):
    for i in range(len(countries['features'])):
        countries['features'][i]['id'] = countries['features'][i]['properties']['iso_a3']
    return countries


def get_country_description(df, country='GBR'):
    adverbs = {
        1: '',
        2: 'quite',
        3: 'very',
        4: 'super',
    }
    audio_expressions = {
        'valence': ['happy', 1],
        'mode': ['moody', -1],
        'energy': ['energetic', 1],
        'danceability': ['dancy', 1],
        'speechiness': ['speechy', 1],
        'acousticness': ['acoustic', 1],
        'instrumentalness': ['instrumental', 1],
        'liveness': ['live', 1],
    }
    country_series = \
        df.loc[df.date == df.date.unique()[-1]].loc[df.iso3 == country][
            [f's_{f}' for f in audio_expressions.keys()]].iloc[0]
    descriptions = []
    for feature, (adjective, sign) in audio_expressions.items():
        # adjective = audio_expressions[f][0]
        # sign = audio_expressions[f][1]
        val = country_series[f's_{feature}'] * sign
        if abs(val) > 1:
            adverb = ''
            for level, a in adverbs.items():
                if abs(val) > level:
                    adverb = a
            description = f'{adverb} {adjective}' if val > 0 else f'not {adverb} {adjective}'
            description = description.replace('  ', ' ').strip()
            descriptions.append(description)
    description_string = ', '.join(descriptions).capitalize()
    return description_string
