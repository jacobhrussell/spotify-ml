import sys
sys.path.append('spotify_ml')
import awsgi
from flask import (Flask, jsonify, request)
from services.spotify_service import SpotifyService
from helpers.env_helper import EnvHelper
from helpers.kmeans_helper import KmeansHelper
from helpers.friday_helper import FridayHelper

app = Flask(__name__)

friday_helper = FridayHelper()
spotify_service = SpotifyService(friday_helper)
env_helper = EnvHelper()
kmeans_helper = KmeansHelper(env_helper)

def lambda_handler(event, context):
    if event.get('path'):
        return awsgi.response(app, event, context)
    else:
        return 400

@app.route('/test', methods=['GET'])
def get_test():
    return jsonify(status=200, response="Hello world")

@app.route('/recommended-songs', methods=['GET'])
def get_recommended_songs():
    track_id = request.args.get("track", None)
    if track_id is not None:
        track_analysis_and_features = spotify_service.get_track_analysis_and_features(track_id)
        recommended_songs = kmeans_helper.recommend_tracks(5, track_id)
        return jsonify(status=200, response=recommended_songs)
    else:
        return jsonify(status=400, response="No track id provided")

@app.route('/search-song', methods=['GET'])
def get_search_song():
    track = request.args.get("track", None)
    artist = request.args.get("artist", None)
    search_results = spotify_service.search_for_track(track, artist)
    return jsonify(status=200, response=search_results)

if __name__ == "__main__":

    # User puts in some search information
    artist = "Mac Miller"
    track = "Blue World"

    # Gets some results
    search_results = spotify_service.search_for_track(track, artist)

    # Picks a track
    track_id = search_results["tracks"]["items"][0]["id"]

    # We get the analysis
    track_analysis_and_features = spotify_service.get_track_analysis_and_features(track_id)

    # We make some recomendations
    recomended_tracks = kmeans_helper.recommend_tracks(5, track_analysis_and_features)
    print("Done")