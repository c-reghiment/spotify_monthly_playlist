"""Core Spotify playlist helper functions shared by CLI and API."""

import os
import secrets
from collections import defaultdict
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import spotipy
from spotipy.oauth2 import SpotifyOAuth


SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET or not SPOTIPY_REDIRECT_URI:
    raise ValueError(
        "Missing environment variables: Ensure SPOTIPY_CLIENT_ID, "
        "SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI are set.")


DEFAULT_SCOPE = 'user-library-read playlist-modify-public playlist-modify-private'


def build_auth_manager(open_browser: bool = False,
                       show_dialog: bool = False,
                       cache_path: Optional[str] = None) -> SpotifyOAuth:
    """Create a SpotifyOAuth manager configured for this app."""

    return SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                        client_secret=SPOTIPY_CLIENT_SECRET,
                        redirect_uri=SPOTIPY_REDIRECT_URI,
                        scope=DEFAULT_SCOPE,
                        open_browser=open_browser,
                        cache_path=cache_path,
                        show_dialog=show_dialog)


def ensure_token(auth_manager: SpotifyOAuth, token_info: Dict) -> Dict:
    """Refresh the token if needed and return the latest token info."""

    if auth_manager.is_token_expired(token_info):
        token_info = auth_manager.refresh_access_token(token_info['refresh_token'])
    return token_info


def get_spotify_client(auth_manager: SpotifyOAuth,
                       token_info: Optional[Dict] = None) -> Tuple[spotipy.Spotify, Dict]:
    """Return an authenticated Spotify client and up-to-date token info."""

    if token_info is None:
        token_info = auth_manager.get_access_token(as_dict=True)

    token_info = ensure_token(auth_manager, token_info)
    sp = spotipy.Spotify(auth=token_info['access_token'])
    return sp, token_info


def create_monthly_playlist(sp: spotipy.Spotify, month_year: str) -> str:
    user_id = sp.current_user()['id']

    playlists = sp.current_user_playlists(limit=50)
    while playlists:
        for playlist in playlists['items']:
            if playlist['name'] == month_year:
                return playlist['id']
        playlists = sp.next(playlists) if playlists['next'] else None

    playlist = sp.user_playlist_create(user_id, month_year, public=False)
    return playlist['id']


def get_saved_tracks_grouped_by_month(sp: spotipy.Spotify) -> Dict[Tuple[int, int], List[str]]:
    monthly_tracks: Dict[Tuple[int, int], List[str]] = defaultdict(list)
    results = sp.current_user_saved_tracks(limit=50)

    while results:
        for item in results['items']:
            added_at = datetime.strptime(item['added_at'], "%Y-%m-%dT%H:%M:%SZ")
            key = (added_at.year, added_at.month)
            monthly_tracks[key].append(item['track']['id'])

        results = sp.next(results) if results['next'] else None

    for tracks in monthly_tracks.values():
        tracks.reverse()

    return monthly_tracks


def chunked(items: Sequence[str], size: int = 100) -> Iterable[Sequence[str]]:
    for start in range(0, len(items), size):
        yield items[start:start + size]


def add_saved_tracks_to_playlist(sp: spotipy.Spotify,
                                 month_year: str,
                                 track_ids: Sequence[str]) -> int:
    playlist_id = create_monthly_playlist(sp, month_year)

    for batch in chunked(track_ids):
        sp.playlist_add_items(playlist_id, batch)

    return len(track_ids)


def get_month_year(months_ago: int = 0) -> Tuple[str, int, int]:
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


def create_playlists_for_months(sp: spotipy.Spotify,
                                retroactive_months: int,
                                monthly_tracks: Optional[Dict[Tuple[int, int], List[str]]] = None
                                ) -> List[Dict[str, object]]:
    if monthly_tracks is None:
        monthly_tracks = get_saved_tracks_grouped_by_month(sp)

    created: List[Dict[str, object]] = []

    for months_ago in range(retroactive_months + 1):
        month_year, year, month = get_month_year(months_ago)
        track_ids = monthly_tracks.get((year, month), [])
        if not track_ids:
            continue

        count = add_saved_tracks_to_playlist(sp, month_year, track_ids)
        created.append({'name': month_year, 'trackCount': count})

    return created


def fetch_all_playlists(sp: spotipy.Spotify) -> List[Dict]:
    playlists: List[Dict] = []
    batch = sp.current_user_playlists(limit=50)

    while batch:
        playlists.extend(batch['items'])
        batch = sp.next(batch) if batch['next'] else None

    return playlists


def generate_state_token() -> str:
    return secrets.token_urlsafe(16)
