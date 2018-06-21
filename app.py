# https://github.com/plamere/spotipy/blob/master/spotipy/util.py
# http://www.acmesystems.it/python_httpd

from bottle import route, run, request
import requests
import spotipy
from spotipy import oauth2
import json
import pprint
import operator

PORT_NUMBER = 8080
SPOTIPY_CLIENT_ID = 'b88d0c99674247bcb826148026417e6f'
SPOTIPY_CLIENT_SECRET = 'fcc139e4e91f4a78aa797bd11a194ce3'
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'
SCOPE = 'user-library-read playlist-modify-public'
CACHE = '.spotipyoauthcache'

playlist_name = 'Carbon'

tej_id = 12129226315
rohan_id = 1250975621
ram_id = 'rammk1999'
yash_id = 'yash.bora'

ids =[tej_id, rohan_id]

sp_oauth = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path=CACHE )

@route('/')
def index():
    access_token = ""
    url = request.url
    code = sp_oauth.parse_response_code(url)
    if code:
        print("Found Spotify auth code in Request URL! Trying to get valid access token...")
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']

    if access_token:
        print("Access token available! Trying to get user information...")
        print(access_token)
        sp = spotipy.Spotify(access_token)


        headers = {
           'Accept': 'application/json',
           'Content-Type': 'application/json',
           'Authorization': 'Bearer ' + access_token,
        }

        total_songs = {}
        for id in ids:
            playlists = requests.get('https://api.spotify.com/v1/users/' + str(id) + '/playlists', headers=headers)
            playlist_json = playlists.json()
            for playlist_whole in playlist_json['items']:
                play_id = playlist_whole['id']
                tracks = requests.get('https://api.spotify.com/v1/users/' + str(id) + '/playlists/' + str(play_id) + '/tracks', headers=headers)
                data = tracks.json()
                for cur_track in data['items']:
                    if cur_track["track"]["id"] in total_songs:
                        total_songs[cur_track["track"]["id"]] += 1
                    else:
                        total_songs[cur_track["track"]["id"]] = 1

        sorted_reverse = sorted(total_songs.items(), key=operator.itemgetter(1), reverse=True)
        #print(sorted_reverse)
        index = 0
        fifty_songs = []
        for k,v in sorted_reverse:
            if index < 50:
                track_info = requests.get('https://api.spotify.com/v1/tracks/' + k, headers=headers)
                track_json = track_info.json()
                name = track_json['name']
                print(name)
                fifty_songs.append(k)
            else:
                break
            index += 1

        sp.user_playlist_create(rohan_id, "Carbon")

        playlists = requests.get('https://api.spotify.com/v1/users/' + str(rohan_id) + '/playlists', headers=headers)
        playlist_json = playlists.json()
        for playlist_whole in playlist_json['items']:
            if playlist_whole['name'] == 'Carbon':
                sp.user_playlist_add_tracks(rohan_id, playlist_whole["id"], fifty_songs)
        stats = list(sp.audio_features(fifty_songs))

        dance_avg = 0
        valence_avg = 0
        energy_avg = 0
        for dictionary in stats:
            dance_avg += float(dictionary['danceability'])
            energy_avg += float(dictionary['energy'])
            valence_avg += float(dictionary['valence'])

        dance_avg /= .5
        valence_avg /= .5
        energy_avg /= .5
        print(dance_avg)
        print(valence_avg)
        print(energy_avg)

    else:
        return htmlForLoginButton()

def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton

def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url

run(host='', port=8080)
