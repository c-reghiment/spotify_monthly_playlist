import spotipy
from spotipy.oauth2 import SpotifyOAuth
import schedule
import time
from datetime import datetime
import webbrowser

# Spotify API credentials (Client ID only)
SPOTIPY_CLIENT_ID = 'your_client_id'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'

scope = 'user-library-read playlist-modify-public playlist-modify-private'


def authenticate_spotify():
    sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                            redirect_uri=SPOTIPY_REDIRECT_URI,
                            scope=scope,
                            open_browser=False)
    auth_url = sp_oauth.get_authorize_url()
    print(f"Please navigate here to authorize: {auth_url}")
    webbrowser.open(auth_url)
    response = input("Enter the URL you were redirected to: ")
    code = sp_oauth.parse_response_code(response)
    token_info = sp_oauth.get_access_token(code)
    sp = spotipy.Spotify(auth=token_info['access_token'])
    return sp


def create_monthly_playlist(sp):
    current_month = datetime.now().strftime('%B %Y')
    user_id = sp.current_user()['id']

    # Check if a playlist for the current month already exists
    playlists = sp.user_playlists(user_id)
    for playlist in playlists['items']:
        if playlist['name'] == current_month:
            playlist_id = playlist['id']
            break
    else:
        # Create a new playlist for the month
        playlist = sp.user_playlist_create(user_id, current_month, public=False)
        playlist_id = playlist['id']

    return playlist_id


def add_saved_tracks_to_playlist(sp):
    playlist_id = create_monthly_playlist(sp)

    # Get the saved tracks
    saved_tracks = sp.current_user_saved_tracks()

    track_ids = [item['track']['id'] for item in saved_tracks['items']]

    # Add tracks to the playlist
    sp.playlist_add_items(playlist_id, track_ids)

    print(f'Added {len(track_ids)} tracks to the playlist "{datetime.now().strftime("%B %Y")}".')


def main():
    sp = authenticate_spotify()
    add_saved_tracks_to_playlist(sp)


if __name__ == "__main__":
    main()
