import base64
import os
from datetime import datetime

import pandas as pd
import requests


class SpotifyScraper:

    def __init__(self) -> None:
        self.auth_value_string = self.get_credentials()
        self.track_list = pd.DataFrame(
            columns=[
                'id', 'data_crawler', 'playlist', 'musica', 'artista',
                'album', 'duracao', 'data_lancamento', 'popularidade'
            ]
        )
        self.data_crawler = datetime.today().date()

    def get_credentials(self) -> str:

        with open('credentials.txt', 'r') as file:
            client_id = file.readline().split()[-1]
            client_secret = file.readline().split()[-1]

        auth_value = client_id + ':' + client_secret
        auth_value = auth_value.encode('ascii')

        auth_value_64 = base64.b64encode(auth_value)
        auth_value_string = auth_value_64.decode('ascii')

        return auth_value_string

    def get_access_token(self) -> str:
        url = 'https://accounts.spotify.com/api/token'

        headers = {'Authorization': f'Basic {self.auth_value_string}',
                   'Content-Type': 'application/x-www-form-urlencoded'}

        payload = {'grant_type': 'client_credentials'}

        response = requests.request(
            'POST', url=url, headers=headers, data=payload)

        access_token = response.json()['access_token']

        return access_token

    def get_playlist_tracks(self, playlist_id):

        self.track_list = pd.DataFrame(
            columns=[
                'id', 'data_crawler', 'playlist', 'musica', 'artista',
                'album', 'duracao', 'data_lancamento', 'popularidade'
            ]
        )

        url = f'https://api.spotify.com/v1/playlists/{playlist_id}'
        headers = {'Authorization': f'Bearer {self.get_access_token()}'}

        response = requests.get(url=url, headers=headers)
        playlist_name = response.json()['name']
        data_tracks = response.json()['tracks']['items']

        for track in data_tracks:

            track_info = track['track']
            id = track_info['id']
            musica = track_info['name']
            artista = self.get_artists(track_info['artists'])
            album = track_info['album']['name']
            duracao = self.milliseconds_to_time(track_info['duration_ms'])
            data_lancamento = track_info['album']['release_date']
            popularidade = track_info['popularity']

            self.track_list.loc[len(self.track_list)] = {
                'id': id,
                'data_crawler': self.data_crawler,
                'playlist': playlist_name,
                'musica': musica,
                'artista': artista,
                'album': album,
                'duracao': duracao,
                'data_lancamento': data_lancamento,
                'popularidade': popularidade,
            }

    def get_track_features(self):

        tracks_ids = ','.join(self.track_list['id'][-50:])

        url = f'https://api.spotify.com/v1/audio-features?ids={tracks_ids}'
        headers = {'Authorization': f'Bearer {self.get_access_token()}'}

        response = requests.get(url=url, headers=headers)

        tracks_features = response.json()['audio_features']

        df_features = pd.DataFrame(tracks_features)
        df_features.drop(
            ['type', 'uri', 'track_href', 'analysis_url', 'duration_ms'],
            axis=1, inplace=True
        )

        self.track_list = pd.merge(
            self.track_list, df_features, on='id', how='inner')

        self.save_playlist_info()

    def milliseconds_to_time(self, milliseconds):
        seconds = (milliseconds // 1000) % 60
        minutes = (milliseconds // (1000 * 60)) % 60

        return f"{minutes:02d}:{seconds:02d}"

    def get_artists(self, artist_dict):

        artist_names = [artist['name'] for artist in artist_dict]

        if len(artist_names) == 1:
            return artist_names[0]

        return " | ".join(artist_names)

    def save_playlist_info(self):
        csv_filename = 'output.csv'
        if not os.path.exists(csv_filename):
            self.track_list.to_csv(csv_filename, index=False)

        else:
            df = pd.read_csv(csv_filename)
            df = pd.concat([df, self.track_list],
                           ignore_index=True, join='inner')
            df.to_csv(csv_filename, index=False)


if __name__ == '__main__':
    spotify = SpotifyScraper()
    with open('playlist.txt', mode='r') as file:
        playlists = file.readlines()

    for id_playlist in playlists:
        id_playlist = id_playlist.rstrip('\n')
        spotify.get_playlist_tracks(id_playlist)
        spotify.get_track_features()

    print("Acabou")
