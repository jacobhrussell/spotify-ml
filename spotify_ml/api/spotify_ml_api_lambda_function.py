import sys
sys.path.append('spotify_ml')
import awsgi
from flask import (Flask, jsonify, request)
from helpers.path_helper import PathHelper

path_helper = PathHelper()


app = Flask(__name__)

def lambda_handler(event, context):
    if event.get('path'):
        return awsgi.response(app, event, context)
    else:
        return 400

@app.route('/get-recommended-songs', methods=['GET'])
def get_recommended_songs():
    recommended_songs = []
    return jsonify(status=200, response=recommended_songs)

@app.route('/search-song', methods=['GET'])
def get_search_song():
    search_results = []
    return jsonify(status=200, response=search_results)

@app.route('/test', methods=['GET'])
def get_test():
    response = "Hello world"
    return jsonify(status=200, response=response)