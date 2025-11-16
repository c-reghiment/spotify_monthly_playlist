import os
from collections import defaultdict
from datetime import datetime

import spotipy
from spotipy.oauth2 import SpotifyOAuth

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

def create_spotify_client():
    """Create a Spotify client with automatic token refresh."""
    auth_manager = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                client_secret=SPOTIPY_CLIENT_SECRET,
                                redirect_uri=SPOTIPY_REDIRECT_URI,
                                scope=scope,
                                open_browser=True)

    # Trigger the auth flow up front so the user can approve access once.
    auth_manager.get_access_token(as_dict=False)
    return spotipy.Spotify(auth_manager=auth_manager)


def create_monthly_playlist(sp, month_year):
    user_id = sp.current_user()['id']

    # Check every page of playlists before creating a new one.
    playlists = sp.current_user_playlists(limit=50)
    while playlists:
        for playlist in playlists['items']:
            if playlist['name'] == month_year:
                return playlist['id']
        playlists = sp.next(playlists) if playlists['next'] else None

    playlist = sp.user_playlist_create(user_id, month_year, public=False)
    return playlist['id']


def get_saved_tracks_grouped_by_month(sp):
    """Fetch saved tracks once and bucket them by (year, month)."""
    monthly_tracks = defaultdict(list)
    results = sp.current_user_saved_tracks(limit=50)

    while results:
        for item in results['items']:
            added_at = datetime.strptime(item['added_at'], "%Y-%m-%dT%H:%M:%SZ")
            key = (added_at.year, added_at.month)
            monthly_tracks[key].append(item['track']['id'])

        results = sp.next(results) if results['next'] else None

    # Spotify returns newest first; reverse to keep the save order intact.
    for tracks in monthly_tracks.values():
        tracks.reverse()

    return monthly_tracks


def chunked(items, size=100):
    for start in range(0, len(items), size):
        yield items[start:start + size]


def add_saved_tracks_to_playlist(sp, month_year, track_ids):
    playlist_id = create_monthly_playlist(sp, month_year)

    for batch in chunked(track_ids):
        sp.playlist_add_items(playlist_id, batch)

    print(f'Added {len(track_ids)} tracks to the playlist "{month_year}".')


def get_month_year(months_ago=0):
    now = datetime.now()
    year = now.year
    month = now.month

    for _ in range(months_ago):
        month -= 1
        if month == 0:
            month = 12
            year -= 1

    target_date = datetime(year, month, 1)
    return target_date.strftime("%B '%y"), year, month


def main():
    sp = create_spotify_client()
    monthly_tracks = get_saved_tracks_grouped_by_month(sp)

    # Get user input for retroactive creation
    retroactive_months = input("Enter the number of past months to create playlists for (0 for only current month): ")
    try:
        retroactive_months = int(retroactive_months)
    except ValueError:
        print("Invalid input. Defaulting to 0.")
        retroactive_months = 0

    for months_ago in range(retroactive_months + 1):
        month_year, year, month = get_month_year(months_ago)
        track_ids = monthly_tracks.get((year, month), [])
        if not track_ids:
            print(f'No tracks to add for {month_year}.')
            continue

        add_saved_tracks_to_playlist(sp, month_year, track_ids)


if __name__ == "__main__":
    main()
