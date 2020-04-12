def get_spotify_credentials():
    return dict(
        cid=open('auth/spotify_cid', 'r').read(),
        secret=open('auth/spotify_secret', 'r').read()
    )


def get_mapbox_token():
    return open('auth/mapbox_token', 'r').read()
