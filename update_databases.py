from database.charts import init_charts_db, run_charts_db
from database.scores import init_scores_db, run_scores_db
from database.tracks import init_tracks_db, run_tracks_db

chart_list = ['Top 200', 'Viral 50']
time_frame_list = ['daily', 'weekly']

if __name__ == '__main__':
    chart = 'Top 200'
    time_frame = 'weekly'

    print('Updating charts db...')
    init_charts_db(chart_list, time_frame_list)
    run_charts_db(chart, time_frame)

    print('Updating tracks db...')
    init_tracks_db()
    run_tracks_db(chart)

    print('Updating scores db...')
    init_scores_db(chart_list, time_frame_list)
    run_scores_db(chart, time_frame)
