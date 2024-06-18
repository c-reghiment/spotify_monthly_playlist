import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta
import webbrowser
import os
from flask import Flask, request
from threading import Thread

# Ensure the environment variables are set
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

# Verification of environment variables
if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET or not SPOTIPY_REDIRECT_URI:
    raise ValueError(
        "Missing environment variables: Ensure SPOTIPY_CLIENT_ID, "
        "SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI are set.")

print("Client ID and Client Secret found.")


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
        print(f"Please navigate here to authorize: {auth_url}")
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


def get_saved_tracks_for_month(sp, year, month):
    results = sp.current_user_saved_tracks(limit=50)
    tracks = []

    while results:
        for item in results['items']:
            added_at = datetime.strptime(item['added_at'], "%Y-%m-%dT%H:%M:%SZ")
            if added_at.year == year and added_at.month == month:
                tracks.append(item['track']['id'])
        if results['next']:
            results = sp.next(results)
        else:
            results = None

    return tracks


def add_saved_tracks_to_playlist(sp, month_year, year, month):
    playlist_id = create_monthly_playlist(sp, month_year)

    # Get the saved tracks for the specified month
    track_ids = get_saved_tracks_for_month(sp, year, month)

    # Add tracks to the playlist in reverse order
    if track_ids:
        track_ids.reverse()
        sp.playlist_add_items(playlist_id, track_ids)
        print(f'Added {len(track_ids)} tracks to the playlist "{month_year}".')
    else:
        print(f'No tracks to add for {month_year}.')


def get_month_year(months_ago=0):
    target_date = datetime.now() - timedelta(days=30 * months_ago)
    return target_date.strftime("%B '%y"), target_date.year, target_date.month


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
        month_year, year, month = get_month_year(months_ago)
        add_saved_tracks_to_playlist(sp, month_year, year, month)


if __name__ == "__main__":
    # Run the Flask app in a separate thread to ensure the main script waits for authentication to complete
    flask_thread = Thread(target=authenticate_spotify)
    flask_thread.start()
    flask_thread.join()  # Wait for the Flask app to complete authentication

    main()
