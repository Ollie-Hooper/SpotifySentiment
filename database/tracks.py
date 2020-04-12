import math
import os
import spotipy
import pandas as pd

from multiprocessing import Process, JoinableQueue

from auth.auth import get_spotify_credentials
from database.tools import Database, handle_db
from functions import time_method


def init_tracks_db():
    with Database('tracks') as tracks_db:
        fields = {
            'id': 'text',
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
        }
        tracks_db.create('audio_features', fields, 'id')


@time_method
def run_tracks_db(chart='Top 200'):
    n_processes = os.cpu_count()

    tracks = get_tracks(chart)

    track_count = len(tracks)

    if track_count > 0:
        tracks_per_pro = math.floor(track_count / n_processes)
        if tracks_per_pro == 0:
            n_processes = track_count
            tracks_per_pro = 1

        sp = get_spotipy()

        processes = []

        db_queue = JoinableQueue()
        Process(target=handle_db, args=('tracks', db_queue,), daemon=True).start()

        for pn in range(1, n_processes + 1):
            if pn == n_processes:
                sub_tracks = tracks[tracks_per_pro * (pn - 1):]
            else:
                sub_tracks = tracks[tracks_per_pro * (pn - 1):tracks_per_pro * pn]
            p = Process(target=update_tracks_db, args=(pn, db_queue, sub_tracks, sp,))
            processes.append(p)
            print(f'Starting process {pn} with {len(sub_tracks)} tracks')
            p.start()
        for p in processes:
            p.join()
        db_queue.join()
        print('Finished updating tracks db!')
    else:
        print('Tracks already up to date!')


def format_tracks_df(df):
    return df.drop(['type', 'uri', 'track_href', 'analysis_url'], axis=1).set_index('id')


def get_audio_features(tracks_list, sp):
    features = sp.audio_features(','.join(tracks_list))

    features = [x for x in features if x]

    if len(features) > 0:
        features_df = pd.DataFrame(features)
        tracks = format_tracks_df(features_df)
        return tracks
    else:
        print(f'{len(tracks_list)} track IDs return empty records')


def update_tracks_db(p, db_queue, tracks_list, sp):
    m = 100

    length = len(tracks_list)
    q = math.floor(length / m)
    r = length % m

    for i in range(0, q + 1):
        if not i == q:
            start = i * m
            end = (i + 1) * m
        else:
            start = q * m
            end = q * m + r

        print(f'{p}: Fetching features for tracks {start + 1} to {end} of {length}')

        s_tracks_list = tracks_list[start:end]

        s_tracks = get_audio_features(s_tracks_list, sp)

        if s_tracks is not None:
            db_queue.put(('insert', 'audio_features', s_tracks))


def get_tracks(chart_name):
    c_name = chart_name.replace(' ', '').lower()

    with Database('charts') as charts_db:
        charts_db.cur.execute(f"SELECT track_id FROM {c_name}_d UNION SELECT track_id FROM {c_name}_w")
        chart_tracks = [x[0] for x in charts_db.cur.fetchall()]

    with Database('tracks') as tracks_db:
        tracks_db.cur.execute("SELECT id FROM audio_features")
        downloaded_tracks = [x[0] for x in tracks_db.cur.fetchall()]

    tracks = [track for track in chart_tracks if track != 'nan' and track not in downloaded_tracks]

    return tracks


def get_spotipy():
    cred = get_spotify_credentials()
    client_credentials_manager = spotipy.SpotifyClientCredentials(client_id=cred['cid'], client_secret=cred['secret'])
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)
