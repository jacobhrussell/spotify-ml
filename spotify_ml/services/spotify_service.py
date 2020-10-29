import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-library-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope), requests_timeout=10)

class SpotifyService:

    def __init__(self, friday_helper):
        self.friday_helper = friday_helper

    def get_new_tracks_analysis_and_features(self):
        new_tracks_analysis_and_features = []
        new_tracks = self.get_new_tracks()

        for track in new_tracks:
            track_analysis_and_features = {}
            track_analysis_and_features['track'] = track
            track_analysis_and_features['analysis'] = self.get_track_analysis(track)
            track_analysis_and_features['features'] = self.get_track_features(track)
            new_tracks_analysis_and_features.append(track_analysis_and_features)
        return new_tracks_analysis_and_features

    def get_track_analysis_and_features(self, track_id):
        track_analysis_and_features = {}
        track = sp.track(track_id)
        track_analysis_and_features['track'] = track
        track_analysis_and_features['analysis'] = self.get_track_analysis(track)
        track_analysis_and_features['features'] = self.get_track_features(track)
        return track_analysis_and_features

    def get_new_tracks(self):
        new_tracks = []
        new_albums = self.get_new_albums()
        for album in new_albums:
            tracks = []
            results = sp.album_tracks(album['id'], limit=50)
            for track in results['items']:
                new_tracks.append(track)

            while results is not None:
                results = sp.next(results)
                if results is not None:
                    for track in tracks:
                        new_tracks.append(track)

        return new_tracks

    def get_new_albums(self):
        friday = self.friday_helper.get_most_recent_friday().strftime("%Y-%m-%d")
        new_albums = []
        results = sp.new_releases(limit=50)
        for album in results['albums']['items']:
            if album['release_date'] == friday:
                new_albums.append(album)
                print(album['name'])

        while results is not None:
            results = sp.next(results['albums'])
            if results is not None:
                for album in results['albums']['items']:
                    if album['release_date'] == friday:
                        new_albums.append(album)
                        print(album['name'])

        return new_albums
    
    def get_album_tracks(self, album):
        album_tracks = sp.album_tracks(album['id'], limit=50)
        return album_tracks

    def get_track_analysis(self, track):
        results = sp.audio_analysis(track['id'])
        return results

    def get_track_features(self, track):
        results = sp.audio_features(track['id'])
        return results

    def search_for_track(self, track, artist):
        search_results = sp.search(q='artist:' + artist + ' track:' + track, type='track')
        return search_results

    def get_track(self, track_id):
        track = sp.track(track_id)
        return track