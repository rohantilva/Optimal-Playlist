from bottle import route, run, request
import requests
import spotipy
from urllib.parse import quote
from spotipy import oauth2
import json
import pprint
import operator
import spotipy.util as util
from flask import Flask, render_template, redirect, request
import configparser
import os

app = Flask(__name__)


cg = configparser.ConfigParser()
cg.read('config.ini')
CLIENT_ID = cg.get('Spotify', 'client_id')
CLIENT_SECRET = cg.get('Spotify', 'client_secret')

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)
PORT = 8080

# Server-side Parameters
REDIRECT_URI = "https://optimalplaylist.herokuapp.com/callback/q"
SCOPE = "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "client_id": CLIENT_ID
}

@app.route("/")
def index():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)

@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    global access_token
    access_token = response_data["access_token"]

    # Auth Step 6: Use the access token to access Spotify API
    global authorization_header
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}
    return render_template('index.html')


@app.route("/#features", methods=['POST'])
def data_handle():
    playlist_name = request.form['playlist_name']
    host_id = request.form['host_user']
    id1 = request.form['id1']
    id2 = request.form['id2']
    ids = []
    ids.append(host_id)
    if id1 is not "":
        ids.append(id1)
    if id2 is not "":
        ids.append(id2)

    total_songs = {}
    for id in ids:
        playlists = requests.get('https://api.spotify.com/v1/users/' + str(id) + '/playlists', headers=authorization_header)
        playlist_json = playlists.json()
        for playlist_whole in playlist_json['items']:
            play_id = playlist_whole['id']
            tracks = requests.get('https://api.spotify.com/v1/users/' + str(id) + '/playlists/' + str(play_id) + '/tracks', headers=authorization_header)
            data = tracks.json()
            for cur_track in data['items']:
                if cur_track["track"]["id"] in total_songs:
                    total_songs[cur_track["track"]["id"]] += 1
                else:
                    total_songs[cur_track["track"]["id"]] = 1

    sorted_reverse = sorted(total_songs.items(), key=operator.itemgetter(1), reverse=True)
    index = 0
    fifty_songs = []
    for k,v in sorted_reverse:
        if index < 50:
            track_info = requests.get('https://api.spotify.com/v1/tracks/' + k, headers=authorization_header)
            track_json = track_info.json()
            name = track_json['name']
            fifty_songs.append(k)
            index += 1
        else:
            break

    sp = spotipy.Spotify(auth=access_token)
    sp.user_playlist_create(host_id, str(playlist_name))

    playlists = requests.get('https://api.spotify.com/v1/users/' + str(host_id) + '/playlists', headers=authorization_header)
    playlist_json = playlists.json()
    for playlist_whole in playlist_json['items']:
        if playlist_whole['name'] == playlist_name:
            sp.user_playlist_add_tracks(host_id, playlist_whole["id"], fifty_songs)

    return redirect('https://open.spotify.com/collection/playlists')


@app.route("/partyform", methods=['POST', 'GET'])
def partyform():
    your_name = request.form['your_name']
    your_user = request.form['your_user']
    partyid = request.form['partyid']
    return render_template("party.html", value=your_name)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
