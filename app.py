import os

from flask import (Flask, redirect, render_template, request, send_from_directory, url_for, jsonify)

app = Flask(__name__)

import os
import json

import genre_prediction
import utils

app = Flask(__name__)


@app.route('/get_similar_genres', methods=['POST'])
def get_songs():
    req_body = request.get_json()
    access_key = os.environ.get('ACCESS_KEY')
    provided_key = req_body.get('access_key')

    if access_key != provided_key:
        return jsonify({"error": "Unauthorized access. Invalid access key."}), 401

    try:
        song_name = req_body.get('song_name')
        artist = req_body.get('artist')

        recommended_tracks = req_body.get('recommended_tracks', [])
        
        given_genre = genre_prediction.predict_genre(song_name, artist)
        given_album_genre = genre_prediction.get_album_genre(song_name, artist)

        for track in recommended_tracks:
            track_name = track.get('track_name')
            artist_name = track.get('artist_name')

            if not track_name or not artist_name:
                return jsonify({"error": "Please provide both song_name and artist_name."}), 400
        
            similar_songs = []

            for track in recommended_tracks:
                song_genre = genre_prediction.predict_genre(track_name, artist_name)
                album_genre = genre_prediction.get_album_genre(track_name, artist_name)

                if given_genre and song_genre:
                    given_genre, song_genre = given_genre.lower(), song_genre.lower()
                if given_album_genre and album_genre:
                    given_album_genre, album_genre = given_album_genre.lower(), album_genre.lower()

                if album_genre and given_album_genre:
                    album_genre, given_album_genre = utils.map_deezer_genre_to_model_genre(album_genre), utils.map_deezer_genre_to_model_genre(given_album_genre)

                similar_song_genre = False
                similar_album_genre = False
                similar1 = False
                similar2 = False

                if given_genre and song_genre:
                    similar_song_genre = (given_genre == song_genre)
                if given_album_genre and album_genre:
                    similar_album_genre = (given_album_genre == album_genre)
                if given_genre and album_genre:
                    similar1 = (given_genre == album_genre)
                if song_genre and given_album_genre:
                    similar2 = (song_genre == given_album_genre)
                
                if similar1 or similar2 or similar_song_genre or similar_album_genre:
                    similar_songs.append(track)


    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"recommended_tracks": similar_songs}), 200


@app.route('/')
def index():
   print('Request for index page received')
   return jsonify({"success": "page loaded, go to /get_similar_genres for recommendations"}), 200


if __name__ == '__main__':
   app.run()
