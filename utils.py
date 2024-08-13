import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

credentials = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=credentials)


def map_deezer_genre_to_model_genre(deezer_genre):
    mapping = {
        'Blues': 'blues',
        'Classical': 'classical',
        'Rap/Hip Hop': 'hip-hop',
        'Jazz': 'jazz',
        'Metal': 'metal',
        'Pop': 'pop',
        'Reggae': 'reggae',
        'Rock': 'rock'
    }
    return mapping.get(deezer_genre, deezer_genre)


def get_song_features(track_id):
    try:
        features = sp.audio_features(track_id)
    except Exception as e:
        print("Error fetching song features")
        return None

    if features:
        return features[0]
    else:
        return None


def get_track_id(track_name, artist_name):
    results = sp.search(q=f'track:{track_name} artist:{artist_name}', type='track')
    items = results['tracks']['items']

    if items:
        return items[0]['id']
    else:
        return None


def get_track_details(uri):
    track_id = uri.split(':')[-1]
    track_info = sp.track(track_id)
    track_name = track_info['name']
    artist_name = track_info['album']['artists'][0]['name'] if track_info['album']['artists'] else 'Unknown Artist'
    return track_name, artist_name
