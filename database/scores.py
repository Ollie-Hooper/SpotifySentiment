import pandas as pd

from database.tools import Database, str_list
from functions import time_method

audio_features = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
                  'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']


def init_scores_db(chart, time_frame):
    t_name = f"{chart.replace(' ', '').lower()}_{time_frame[0]}"
    fields = {
        'id': 'text',
        'date': 'text',
        'country': 'text',
        'danceability': 'integer',
        'energy': 'integer',
        'key': 'integer',
        'loudness': 'integer',
        'mode': 'integer',
        'speechiness': 'integer',
        'acousticness': 'integer',
        'instrumentalness': 'integer',
        'liveness': 'integer',
        'valence': 'integer',
        'tempo': 'integer',
        'duration_ms': 'integer',
        'time_signature': 'integer',
        's_danceability': 'integer',
        's_energy': 'integer',
        's_key': 'integer',
        's_loudness': 'integer',
        's_mode': 'integer',
        's_speechiness': 'integer',
        's_acousticness': 'integer',
        's_instrumentalness': 'integer',
        's_liveness': 'integer',
        's_valence': 'integer',
        's_tempo': 'integer',
        's_duration_ms': 'integer',
        's_time_signature': 'integer',
    }
    with Database('scores') as db:
        db.create(t_name, fields, 'id')


@time_method
def run_scores_db(chart='Top 200', time_frame='weekly'):
    dates = get_dates(chart, time_frame)
    if len(dates) > 0:
        charts_df = get_charts_df(dates, chart, time_frame)
        tracks = charts_df['track_id'].unique()
        tracks_df = get_tracks_df(tracks)
        merged_df = get_merged_df(charts_df, tracks_df)
        del charts_df
        del tracks_df
        scores_df = format_scores_df(calculate_scores(merged_df))
        del merged_df
        upload_scores_df(scores_df, chart, time_frame)
        del scores_df
        update_standardized_scores(chart, time_frame)
        print('Finished updating scores db!')
    else:
        print('Scores db already up to date!')


def update_standardized_scores(chart, time_frame):
    t_name = f"{chart.replace(' ', '').lower()}_{time_frame[0]}"
    with Database('scores') as db:
        scores_df = db.select(t_name, ['id', 'country', *audio_features])
        scores_df = standardize_scores(scores_df)
        db.update(t_name, scores_df[[f's_{k}' for k in audio_features]])


def standardize_scores(df):
    mean = df.groupby('country').mean()
    std = df.groupby('country').std()
    df = ((df.reset_index().set_index(['id', 'country'])[
                      audio_features] - mean) / std).reset_index().set_index('id')
    return df.rename(columns={k: f's_{k}' for k in audio_features})


def get_charts_df(dates, chart, time_frame):
    t_name = f"{chart.replace(' ', '').lower()}_{time_frame[0]}"
    with Database('charts') as db:
        charts_df = db.select(t_name, ['date', 'country', 'track_id'], {'date': str_list(dates)})
    charts_df['date'] = pd.to_datetime(charts_df['date'])
    charts_df.set_index(['date', 'country'], inplace=True)
    return charts_df


def get_tracks_df(tracks):
    t_name = 'audio_features'
    with Database('tracks') as db:
        tracks_df = db.select(t_name, filters={'id': str_list(tracks)})
    return tracks_df


def get_merged_df(charts_df, tracks_df):
    merged_df = pd.merge(charts_df, tracks_df, how="inner", left_on='track_id', right_index=True)
    return merged_df


def calculate_scores(merged_df):
    scores_df = merged_df.groupby(['date', 'country']).mean()
    return scores_df


def format_scores_df(scores_df):
    scores_df.reset_index(inplace=True)
    scores_df['date'] = scores_df['date'].apply(lambda x: x.strftime('%m/%d/%Y'))
    scores_df['id'] = scores_df['date'] + '|' + scores_df['country']
    return scores_df.set_index('id')


def upload_scores_df(scores_df, chart, time_frame):
    t_name = f"{chart.replace(' ', '').lower()}_{time_frame[0]}"
    with Database('scores') as db:
        db.insert(t_name, scores_df)


def get_dates(chart, time_frame):
    t_name = f"{chart.replace(' ', '').lower()}_{time_frame[0]}"
    with Database('scores') as scores_db:
        scores_db.cur.execute(f"SELECT DISTINCT date FROM {t_name}")
        calculated_dates = [x[0] for x in scores_db.cur.fetchall()]

    with Database('charts') as charts_db:
        charts_db.cur.execute(f"SELECT DISTINCT date FROM {t_name}")
        avail_dates = [x[0] for x in charts_db.cur.fetchall()]

    dates = [date for date in avail_dates if date not in calculated_dates]

    return dates
