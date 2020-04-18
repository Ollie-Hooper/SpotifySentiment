import math
import os
import time
import requests
import pandas as pd

from io import StringIO
from datetime import timedelta
from lxml import html
from multiprocessing import Process, JoinableQueue

from database.tools import Database, handle_db
from functions import time_method

t200_url = "https://spotifycharts.com/regional"
v50_url = "https://spotifycharts.com/viral"


@time_method
def run_charts_db(chart='Top 200', time_frame='weekly'):
    n_processes = os.cpu_count()

    dates = get_dates(chart, time_frame)

    date_count = len(dates)

    if date_count > 0:
        dates_per_pro = math.floor(date_count / n_processes)

        processes = []

        db_queue = JoinableQueue()
        Process(target=handle_db, args=('charts', db_queue,), daemon=True).start()

        if dates_per_pro == 0:
            n_processes = date_count
            dates_per_pro = 1

        for pn in range(1, n_processes + 1):
            if pn == n_processes:
                sub_dates = dates[dates_per_pro * (pn - 1):]
            else:
                sub_dates = dates[dates_per_pro * (pn - 1):dates_per_pro * pn]
            p = Process(target=update_charts_db, args=(pn, db_queue, sub_dates, chart,))
            processes.append(p)
            print(f'Starting process {pn} with date {sub_dates[0]} to {sub_dates[-1]}')
            p.start()
        for p in processes:
            p.join()
        db_queue.join()
        print('Finished updating charts db!')
    else:
        print('Charts already up to date!')


def update_charts_db(p, db_queue, dates, chart_name, time_frame='weekly'):
    country_meta = pd.read_csv('data/country_meta.csv')

    for i in range(len(dates)):
        date = dates[i]

        print(f'{p}: Running date: {date} - {i+1} of {len(dates)}')
        for country in country_meta['country']:
            country_name = country_meta[country_meta['country'] == country]['name'].iloc[0]
            if chart_name == 'Top 200':
                top200 = format_charts_df(get_chart(date, country, country_name, 'Top 200', t200_url, time_frame))
                if top200 is not None:
                    db_queue.put(('insert', f'top200_{time_frame[0]}', top200))
            elif chart_name == 'Viral 50':
                viral50 = format_charts_df(get_chart(date, country, country_name, 'Viral 50', v50_url, time_frame))
                if viral50 is not None:
                    db_queue.put(('insert', f'viral50_{time_frame[0]}', viral50))


def format_charts_df(df):
    if df is not None:
        if 'Streams' not in df.columns:
            df['Streams'] = 0
        df = df.rename(columns={
            'Position': 'pos',
            'Track Name': 'track_name',
            'Artist': 'artist',
            'Streams': 'streams',
        })
        df['track_id'] = df['URL'].apply(lambda x: str(x).split('/')[-1])
        df = df[['date', 'country', 'pos', 'track_name', 'artist', 'streams', 'track_id']]
        df['id'] = df['date'] + '|' + df['country'] + '|' + df['pos'].apply(lambda x: str(x))
        return df.set_index('id')


def init_charts_db(charts, time_frames):
    fields = {
        'id': 'text',
        'date': 'text',
        'country': 'text',
        'pos': 'integer',
        'track_name': 'text',
        'artist': 'text',
        'streams': 'int',
        'track_id': 'text'
    }
    with Database('charts') as charts_db:
        for chart in charts:
            for time_frame in time_frames:
                t_name = f"{chart.replace(' ', '').lower()}_{time_frame[0]}"
                charts_db.create(t_name, fields, 'id')


def download_chart(date, country, url, time_frame, chart_name):
    if chart_name == 'Top 200':
        chart = pd.read_csv(
            StringIO(requests.get(f"{url}/{country}/{time_frame}/{date}/download").text),
            header=1)
    elif chart_name == 'Viral 50':
        chart = pd.read_csv(
            StringIO(requests.get(f"{url}/{country}/{time_frame}/{date}/download").text),
            header=0)
    else:
        raise TypeError('Invalid chart_name')
    return chart


def get_chart(date, country, country_name, chart_name, url, time_frame='weekly'):
    try:
        s_ts = time.time()
        if time_frame == 'weekly':
            if chart_name == 'Top 200':
                date_str = f"{(pd.to_datetime(date) - timedelta(6)).strftime('%Y-%m-%d')}--{(pd.to_datetime(date) + timedelta(1)).strftime('%Y-%m-%d')}"
            elif chart_name == 'Viral 50':
                date_str = f"{pd.to_datetime(date).strftime('%Y-%m-%d')}--{pd.to_datetime(date).strftime('%Y-%m-%d')}"
        elif time_frame == 'daily':
            date_str = pd.to_datetime(date).strftime('%Y-%m-%d')
        else:
            raise TypeError('Invalid time_frame')
        print(f'Downloading {chart_name} for {country_name}, {date}')
        df = download_chart(date_str, country, url, time_frame, chart_name)
        print(f'Downloaded {chart_name} for {country_name}, {date} - took %2.2f seconds' % (time.time() - s_ts))
        df['date'] = date
        df['country'] = country
        return df
    except:
        print(f'Failed to download {chart_name} for {country_name}, {date}')


def get_dates(chart_name, time_frame):
    url = f"https://spotifycharts.com/regional/global/{time_frame}"

    page = requests.get(url)

    tree = html.fromstring(page.text)

    avail_dates = list(tree.xpath("//div[@class='responsive-select'][@data-type='date']/ul/li/text()"))

    t_name = f"{chart_name.replace(' ', '').lower()}_{time_frame[0]}"

    with Database('charts') as charts_db:
        charts_db.cur.execute(f"SELECT DISTINCT date FROM {t_name}")
        downloaded_dates = [x[0] for x in charts_db.cur.fetchall()]

    dates = [date for date in avail_dates if date not in downloaded_dates]

    return dates
