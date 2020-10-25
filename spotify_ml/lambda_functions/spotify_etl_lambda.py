import sys
sys.path.append('spotify_ml')

from services.spotify_service import SpotifyService
import boto3
import json
import pandas as pd
import io
import gzip

session = boto3.Session()

spotify_service = SpotifyService()

def lambda_handler(event, context):

    print("Getting New Music Friday analysis from Spotify")
    new_tracks_analysis_and_features = spotify_service.get_new_tracks_analysis_and_features()

    print("Transforming data")
    transformed_data = []

    # header row
    header_row = ['track_id', 'danceability', 'energy', 'key', 'loudness', 'mode', 
    'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 
    'num_samples', 'duration', 'end_of_fade_in', 'start_of_fade_out', 'loudness', 
    'tempo', 'tempo_confidence', 'time_signature', 'time_signature_confidence', 'key', 'key_confidence', 'mode', 'mode_confidence']

    for track_feature_analysis in new_tracks_analysis_and_features:
        data = []
        data.append(track_feature_analysis['track']['id'])
        data.append(track_feature_analysis['features'][0]['danceability'])
        data.append(track_feature_analysis['features'][0]['energy'])
        data.append(track_feature_analysis['features'][0]['key'])
        data.append(track_feature_analysis['features'][0]['loudness'])
        data.append(track_feature_analysis['features'][0]['mode'])
        data.append(track_feature_analysis['features'][0]['speechiness'])
        data.append(track_feature_analysis['features'][0]['acousticness'])
        data.append(track_feature_analysis['features'][0]['instrumentalness'])
        data.append(track_feature_analysis['features'][0]['liveness'])
        data.append(track_feature_analysis['features'][0]['valence'])
        data.append(track_feature_analysis['features'][0]['tempo'])
        data.append(track_feature_analysis['analysis']['track']['num_samples'])
        data.append(track_feature_analysis['analysis']['track']['duration'])
        data.append(track_feature_analysis['analysis']['track']['end_of_fade_in'])
        data.append(track_feature_analysis['analysis']['track']['start_of_fade_out'])
        data.append(track_feature_analysis['analysis']['track']['loudness'])
        data.append(track_feature_analysis['analysis']['track']['tempo'])
        data.append(track_feature_analysis['analysis']['track']['tempo_confidence'])
        data.append(track_feature_analysis['analysis']['track']['time_signature'])
        data.append(track_feature_analysis['analysis']['track']['time_signature_confidence'])
        data.append(track_feature_analysis['analysis']['track']['key'])
        data.append(track_feature_analysis['analysis']['track']['key_confidence'])
        data.append(track_feature_analysis['analysis']['track']['mode'])
        data.append(track_feature_analysis['analysis']['track']['mode_confidence'])
        transformed_data.append(data)

    # put transformed data into a pandas data fame
    # this will help us stream into S3
    spotify_df = pd.DataFrame(transformed_data)
    spotify_df.columns = header_row

    print("Putting data in S3")
    # Getting S3 bucket
    s3 = session.resource('s3')
    bucket_name = 'dev-sagemaker-input-bucket'
    bucket = s3.Bucket(bucket_name)

    # Deleting old object in bucket
    s3.Object(bucket_name, 'spotify_input.json').delete()

    # Putting new object in bucket
    # write df to string stream
    csv_buffer = io.StringIO()
    spotify_df.to_csv(csv_buffer, index=False)

    # reset stream position
    csv_buffer.seek(0)

    # create binary stream
    gz_buffer = io.BytesIO()

    # compress string stream using gzip
    with gzip.GzipFile(mode="w", fileobj=gz_buffer) as gz_file:
        gz_file.write(bytes(csv_buffer.getvalue(), 'utf-8'))

    # write stream to S3
    s3_object = s3.Object(bucket_name, 'spotify_input.csv')
    s3_object.put(Body=gz_buffer.getvalue())

if __name__ == "__main__":
    lambda_handler(None, None)