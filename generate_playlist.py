from flask import Flask, redirect, request, session, url_for, render_template
from spotipy import Spotify
from spotipy.oauth2 import SpotifyPKCE
import os 
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SESSION_COOKIE_NAME"] = "Spotiplaylist"

# Replace with app's client ID from Spotify Developer and redirect URI
CLIENT_ID = ""
REDIRECT_URI = "http://localhost:5000/callback"  

# Initialize the SpotifyPKCE object
sp_oauth = SpotifyPKCE(CLIENT_ID, REDIRECT_URI, scope="user-library-read playlist-read-private playlist-modify-public playlist-modify-private")

@app.route("/")
def index():
    if not session.get("token_info"):
        return render_template("index.html")

    sp = Spotify(auth=session["token_info"])
    playlists = sp.current_user_playlists()

    with open("songs.json", "r") as json_file:
        songs = json.load(json_file)

    playlist_name = "Mood playlist"
    playlist_description = "A playlist generated from a JSON file"
    user_id = sp.me()["id"]
    playlist = sp.user_playlist_create(user_id, playlist_name, public=False, description=playlist_description)

    for song in songs:
        track_name = song["track_name"]
        artist_name = song["artist_name"]

        search_results = sp.search(q=f"track:{track_name} artist:{artist_name}", type="track")

        if search_results["tracks"]["items"]:
            track_uri = search_results["tracks"]["items"][0]["uri"]
            sp.playlist_add_items(playlist["id"], [track_uri])

    return render_template("playlists.html", playlists=playlists)

@app.route("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    token_info = sp_oauth.get_access_token(request.args["code"])
    session["token_info"] = token_info
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.pop("token_info", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
