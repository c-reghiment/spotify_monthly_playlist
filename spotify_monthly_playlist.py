import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta
import webbrowser
import os
from flask import Flask, request

# Ensure the environment variables are set
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

# Verification of environment variables
if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET or not SPOTIPY_REDIRECT_URI:
    raise ValueError(
        "Missing environment variables: "
        "Ensure SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI are set.")

print("Client ID and Client Secret found.")
print(f"Client ID: {SPOTIPY_CLIENT_ID}")
print(f"Client Secret: {SPOTIPY_CLIENT_SECRET}")

scope = 'user-library-read playlist-modify-public playlist-modify-private'

app = Flask(__name__)
sp_oauth = None
cached_token = None


@app.route('/callback')
def callback():
    global cached_token
    code = request.args.get('code')
    cached_token = sp_oauth.get_access_token(code, as_dict=False)
    return "You can close this tab and return to the script."


def authenticate_spotify():
    global sp_oauth, cached_token
    sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                            client_secret=SPOTIPY_CLIENT_SECRET,
                            redirect_uri=SPOTIPY_REDIRECT_URI,
                            scope=scope,
                            open_browser=False)

    cached_token = sp_oauth.get_cached_token()
    if not cached_token:
        auth_url = sp_oauth.get_authorize_url()
        webbrowser.open(auth_url)
        app.run(port=8888)
    else:
        cached_token = cached_token['access_token']


def create_monthly_playlist(sp, month_year):
    user_id = sp.current_user()['id']

    # Check if a playlist for the given month already exists
    playlists = sp.user_playlists(user_id)
    for playlist in playlists['items']:
        if playlist['name'] == month_year:
            playlist_id = playlist['id']
            break
    else:
        # Create a new playlist for the month
        playlist = sp.user_playlist_create(user_id, month_year, public=False)
        playlist_id = playlist['id']

    return playlist_id


def add_saved_tracks_to_playlist(sp, month_year):
    playlist_id = create_monthly_playlist(sp, month_year)

    # Get the saved tracks
    saved_tracks = sp.current_user_saved_tracks()

    track_ids = [item['track']['id'] for item in saved_tracks['items']]

    # Add tracks to the playlist
    sp.playlist_add_items(playlist_id, track_ids)

    print(f'Added {len(track_ids)} tracks to the playlist "{month_year}".')


def get_month_year(months_ago=0):
    target_date = datetime.now() - timedelta(days=30 * months_ago)
    return target_date.strftime("%B '%y")


def main():
    authenticate_spotify()
    sp = spotipy.Spotify(auth=cached_token)

    # Get user input for retroactive creation
    retroactive_months = input("Enter the number of past months to create playlists for (0 for only current month): ")
    try:
        retroactive_months = int(retroactive_months)
    except ValueError:
        print("Invalid input. Defaulting to 0.")
        retroactive_months = 0

    for months_ago in range(retroactive_months + 1):
        month_year = get_month_year(months_ago)
        add_saved_tracks_to_playlist(sp, month_year)


if __name__ == "__main__":
    main()
