import sys
sys.path.append('spotify_ml')
import boto3
import gzip
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

class KmeansHelper:

    def __init__(self, env_helper):
        self.env_helper = env_helper

    def train_model(self, scaled_track_data):
        kmeans = KMeans(n_clusters=5, random_state=42)
        kmeans.fit(scaled_track_data)
        return kmeans
    
    def get_data_source(self):
        session = boto3.Session()
        s3_client = session.client('s3')
        bucket_name = self.env_helper.get_env() + '-spotify-analysis-bucket'
        content_object = s3_client.get_object(Bucket=bucket_name, Key='spotify_analysis.csv')
        gz = gzip.GzipFile(fileobj=content_object['Body'])
        track_data = pd.read_csv(gz, dtype=str)
        return track_data
    
    def recommend_tracks(self, num_to_recommend, track_analysis_and_features):

        data = self.get_data_source()

        # remove the id column to add back later after the transformation
        track_id_column = data['track_id']
        data = data.drop('track_id', 1)

        scaler = StandardScaler()
        scaled_data = pd.DataFrame(scaler.fit_transform(data))

        kmeans_model = self.train_model(scaled_data)

        distances_from_centroid = self.get_distances_from_centroid(kmeans_model, scaled_data)

        clusters = self.get_clusters(kmeans_model, scaled_data)

        # add clusters column
        scaled_data["clusters"] = clusters

        # add distance from centroid column
        minimum_distances = []
        index = 0
        for value in clusters:
            minimum_distances.append(distances_from_centroid[index][value])
            index = index + 1
        scaled_data['distance_to_centroid'] = minimum_distances

        # add the id column back
        scaled_data['track_id'] = track_id_column
        
        # get inference
        track_df = self.get_track_df(track_analysis_and_features)
        scaled_track = pd.DataFrame(scaler.transform(track_df))
        inference = self.get_inference(scaled_track, kmeans_model)
        distance = self.get_distance_from_centroid(kmeans_model, scaled_track, inference)

        # recommend tracks
        recommended_track_ids = []
        is_in_cluster = scaled_data['clusters'] == inference[0]
        cluster_neighbors = scaled_data[is_in_cluster]
        distances = cluster_neighbors['distance_to_centroid']
        for i in range(num_to_recommend):
            index = self.get_closest_value(distances, distance)
            recommended_track_ids.append(scaled_data.iloc[[distances.index[index]]]["track_id"].values[0])
            distances = distances.drop([distances.index[index]])
        return recommended_track_ids

    def get_inference(self, scaled_track, kmeans):
        inference = kmeans.predict(scaled_track)
        return inference

    def get_distance_from_centroid(self, kmeans, scaled_data, inference):
        distance = kmeans.transform(scaled_data)[0][inference]
        return distance

    def get_distances_from_centroid(self, kmeans, scaled_data):
        copy_data = scaled_data
        distances = kmeans.transform(copy_data)
        return distances
    
    def get_clusters(self, kmeans, scaled_data):
        clusters = kmeans.predict(scaled_data)
        return clusters

    def get_closest_value(self, lst, value):
        closest_value = min(range(len(lst.values)), key=lambda i: abs(lst.values[i]-value))
        return closest_value

    def get_track_df(self, track_analysis_and_features):
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
        track_df = pd.DataFrame(np.row_stack(tracks))
        return track_df