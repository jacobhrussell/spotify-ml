import sys
sys.path.append('spotify_ml')

import boto3
import gzip
import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from services.spotify_service import SpotifyService

scope = "user-library-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope), requests_timeout=10)

#sklearn imports
from sklearn.decomposition import PCA #Principal Component Analysis
from sklearn.manifold import TSNE #T-Distributed Stochastic Neighbor Embedding
from sklearn.cluster import KMeans #K-Means Clustering
from sklearn.preprocessing import StandardScaler #used for 'Feature Scaling'

#plotly imports
import plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot


session = boto3.Session()

spotify_service = SpotifyService()

def lambda_handler(event, context):

    print("Getting data from S3")
    s3_client = session.client('s3')
    bucket_name = 'dev-sagemaker-input-bucket'
    content_object = s3_client.get_object(Bucket=bucket_name, Key='spotify_input.csv')
    gz = gzip.GzipFile(fileobj=content_object['Body'])
    track_data = pd.read_csv(gz, dtype=str)

    # remove the id column to add back later after the transformation
    track_id_column = track_data['track_id']
    track_data = track_data.drop('track_id', 1)

    # scale data
    scaler = StandardScaler()
    scaled_data = pd.DataFrame(scaler.fit_transform(track_data))

    # train kmeans
    kmeans = KMeans(n_clusters=5, random_state=42)
    kmeans.fit(scaled_data)

    # get distances from centroids
    copy_data = scaled_data
    all_distances = kmeans.transform(copy_data)

    # get clusters
    clusters = kmeans.predict(scaled_data)
    scaled_data["clusters"] = clusters

    # add distance from centroid column
    minimum_distances = []
    index = 0
    for value in clusters:
        minimum_distances.append(all_distances[index][value])
        index = index + 1
    scaled_data['distance_to_centroid'] = minimum_distances

    # add the id column back
    scaled_data['track_id'] = track_id_column

    # get track
    artist = "Mac Miller"
    track = "Blue World"
    search_results = sp.search(q='artist:' + artist + ' track:' + track, type='track')
    track_id = search_results["tracks"]["items"][0]["id"]
    track_analysis_and_features = spotify_service.get_track_analysis_and_features(track_id)
    tracks = []
    track = []
    track.append(track_analysis_and_features['features'][0]['danceability'])
    track.append(track_analysis_and_features['features'][0]['energy'])
    track.append(track_analysis_and_features['features'][0]['key'])
    track.append(track_analysis_and_features['features'][0]['loudness'])
    track.append(track_analysis_and_features['features'][0]['mode'])
    track.append(track_analysis_and_features['features'][0]['speechiness'])
    track.append(track_analysis_and_features['features'][0]['acousticness'])
    track.append(track_analysis_and_features['features'][0]['instrumentalness'])
    track.append(track_analysis_and_features['features'][0]['liveness'])
    track.append(track_analysis_and_features['features'][0]['valence'])
    track.append(track_analysis_and_features['features'][0]['tempo'])
    track.append(track_analysis_and_features['analysis']['track']['num_samples'])
    track.append(track_analysis_and_features['analysis']['track']['duration'])
    track.append(track_analysis_and_features['analysis']['track']['end_of_fade_in'])
    track.append(track_analysis_and_features['analysis']['track']['start_of_fade_out'])
    track.append(track_analysis_and_features['analysis']['track']['loudness'])
    track.append(track_analysis_and_features['analysis']['track']['tempo'])
    track.append(track_analysis_and_features['analysis']['track']['tempo_confidence'])
    track.append(track_analysis_and_features['analysis']['track']['time_signature'])
    track.append(track_analysis_and_features['analysis']['track']['time_signature_confidence'])
    track.append(track_analysis_and_features['analysis']['track']['key'])
    track.append(track_analysis_and_features['analysis']['track']['key_confidence'])
    track.append(track_analysis_and_features['analysis']['track']['mode'])
    track.append(track_analysis_and_features['analysis']['track']['mode_confidence'])
    tracks.append(track)

    # draw inference from an array
    track_df = pd.DataFrame(np.row_stack(tracks))

    scaled_tracks = pd.DataFrame(scaler.transform(track_df))
    inference = kmeans.predict(scaled_tracks)
    distance = kmeans.transform(scaled_tracks)[0][inference]

    # recommend 5 tracks
    # filter list to only tracks in the inference cluster
    num_tracks_to_recommend = 5
    recommended_track_ids = []
    is_in_cluster = scaled_data['clusters'] == inference[0]
    cluster_neighbors = scaled_data[is_in_cluster]
    distances = cluster_neighbors['distance_to_centroid']
    for i in range(num_tracks_to_recommend):
        index = get_closest_value(distances, distance)
        recommended_track_ids.append(scaled_data.iloc[[distances.index[index]]]["track_id"].values[0])
        distances = distances.drop([distances.index[index]])

    recommended_tracks = []
    for track_id in recommended_track_ids:
        track = sp.track(track_id)
        info = track["name"] + " -- " + track["album"]["artists"][0]["name"] 
        recommended_tracks.append(info)

    print("Done")

def get_closest_value(lst, value):
    to_return = min(range(len(lst.values)), key=lambda i: abs(lst.values[i]-value))
    return to_return

if __name__ == "__main__":
    lambda_handler(None, None)