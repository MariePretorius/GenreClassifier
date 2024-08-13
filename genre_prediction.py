import requests
from pydub import AudioSegment
import os
from transformers import pipeline
from io import BytesIO
import librosa


def get_deezer_preview_url(song_name, artist_name):
    query = f"{song_name} {artist_name}"
    url = f"https://api.deezer.com/search?q={query}"
    response = requests.get(url)
    data = response.json()

    if data['total'] > 0:
        preview_url = data['data'][0]['preview']
        return preview_url
    else:
        return None


def download_and_convert_to_wav(audio_url):
    response = requests.get(audio_url)
    audio = AudioSegment.from_file(BytesIO(response.content), format='mp3')
    audio_buffer = BytesIO()
    audio.export(audio_buffer, format='wav')
    audio_buffer.seek(0)
    return audio_buffer


def audio_buffer_to_numpy(audio_buffer):
    audio_buffer.seek(0)
    y, sr = librosa.load(audio_buffer, sr=None)
    return y, sr


def predict_genre(song_name, artist_name):
    preview_url = get_deezer_preview_url(song_name, artist_name)

    if preview_url is None:
        return ""

    audio_buffer = download_and_convert_to_wav(preview_url)
    y, sr = audio_buffer_to_numpy(audio_buffer)

    audio_classification = pipeline("audio-classification", model="dima806/music_genres_classification")
    genre_prediction = audio_classification(y, sampling_rate=sr)

    return genre_prediction[0]['label']


def get_album_genre(song_name, artist_name):
    query = f"{song_name} {artist_name}"
    url = f"https://api.deezer.com/search?q={query}"
    response = requests.get(url)
    data = response.json()

    if data['total'] > 0:
        song_id = data['data'][0]['id']
        song_url = f"https://api.deezer.com/track/{song_id}"
        song_response = requests.get(song_url)
        song_data = song_response.json()

        if 'album' in song_data:
            album_id = song_data['album']['id']
            album_url = f"https://api.deezer.com/album/{album_id}"
            album_response = requests.get(album_url)
            album_data = album_response.json()

            if 'genres' in album_data and 'data' in album_data['genres'] and len(album_data['genres']['data']) > 0:
                genre_name = album_data['genres']['data'][0]['name']
                return genre_name
            else:
                return ""
        else:
            return ""
    else:
        return ""
