"""Flask API exposing Spotify playlist automation endpoints."""

import os

from flask import Flask, jsonify, redirect, request, session
from flask_cors import CORS

from playlist_core import (build_auth_manager, create_playlists_for_months,
                           fetch_all_playlists, generate_state_token,
                           get_month_year, get_saved_tracks_grouped_by_month,
                           get_spotify_client)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret')
CORS(app, supports_credentials=True)

FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
AUTH_SUCCESS_REDIRECT = os.getenv('AUTH_SUCCESS_REDIRECT', f'{FRONTEND_URL}/auth-success')
STATE_SESSION_KEY = 'spotify_auth_state'
TOKEN_SESSION_KEY = 'spotify_token_info'

# Single auth manager reused for the process.
auth_manager = build_auth_manager(open_browser=False)


def require_spotify_client():
    token_info = session.get(TOKEN_SESSION_KEY)
    if not token_info:
        return None

    sp, token_info = get_spotify_client(auth_manager, token_info)
    session[TOKEN_SESSION_KEY] = token_info
    return sp


@app.get('/auth/login')
def auth_login():
    state = generate_state_token()
    session[STATE_SESSION_KEY] = state
    auth_url = auth_manager.get_authorize_url(state=state)
    return jsonify({'authUrl': auth_url})


@app.get('/auth/callback')
def auth_callback():
    state = request.args.get('state')
    if not state or state != session.get(STATE_SESSION_KEY):
        return 'Invalid or missing state parameter.', 400

    code = request.args.get('code')
    if not code:
        return 'Missing authorization code.', 400

    token_info = auth_manager.get_access_token(code, as_dict=True)
    session[TOKEN_SESSION_KEY] = token_info

    return redirect(AUTH_SUCCESS_REDIRECT)


@app.get('/auth/status')
def auth_status():
    authenticated = TOKEN_SESSION_KEY in session
    return jsonify({'authenticated': authenticated})


@app.post('/auth/logout')
def auth_logout():
    session.pop(TOKEN_SESSION_KEY, None)
    session.pop(STATE_SESSION_KEY, None)
    return jsonify({'authenticated': False})


@app.get('/api/playlists')
def list_playlists():
    sp = require_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated.'}), 401

    playlists = fetch_all_playlists(sp)
    return jsonify(playlists)


@app.get('/api/monthly-preview')
def monthly_preview():
    sp = require_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated.'}), 401

    months = request.args.get('months', default='0')
    try:
        months = int(months)
    except ValueError:
        return jsonify({'error': 'Invalid months parameter.'}), 400

    grouped = get_saved_tracks_grouped_by_month(sp)
    preview = []
    for months_ago in range(months + 1):
        month_year, year, month = get_month_year(months_ago)
        preview.append({
            'name': month_year,
            'trackCount': len(grouped.get((year, month), []))
        })

    return jsonify(preview)


@app.post('/api/create-playlists')
def create_playlists():
    sp = require_spotify_client()
    if not sp:
        return jsonify({'error': 'Not authenticated.'}), 401

    payload = request.get_json(force=True, silent=True) or {}
    months = payload.get('months', 0)
    try:
        months = int(months)
    except ValueError:
        return jsonify({'error': 'Invalid months value.'}), 400

    grouped = get_saved_tracks_grouped_by_month(sp)
    created = create_playlists_for_months(sp, months, grouped)

    return jsonify({'created': created})


if __name__ == '__main__':
    app.run(port=5000, debug=True)
