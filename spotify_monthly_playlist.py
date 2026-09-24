"""CLI entry point for building Spotify monthly playlists."""

from playlist_core import (build_auth_manager, create_playlists_for_months,
                           get_month_year, get_saved_tracks_grouped_by_month,
                           get_spotify_client)


def login():
    """Run the OAuth login flow and return an authenticated client."""

    auth_manager = build_auth_manager(open_browser=True, show_dialog=True)
    sp, token_info = get_spotify_client(auth_manager)
    return auth_manager, sp, token_info


def prompt_retroactive_months() -> int:
    retroactive_months = input("Enter the number of past months to create playlists for (0 for only current month): ")
    try:
        return int(retroactive_months)
    except ValueError:
        print("Invalid input. Defaulting to 0.")
        return 0


def main():
    _, sp, _ = login()
    monthly_tracks = get_saved_tracks_grouped_by_month(sp)

    retroactive_months = prompt_retroactive_months()

    created = create_playlists_for_months(sp, retroactive_months, monthly_tracks)

    if not created:
        for months_ago in range(retroactive_months + 1):
            month_year, _, _ = get_month_year(months_ago)
            print(f'No tracks to add for {month_year}.')
        return

    for playlist in created:
        print(f"Added {playlist['trackCount']} tracks to the playlist \"{playlist['name']}\".")


if __name__ == "__main__":
    main()
