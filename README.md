# Spotify Monthly Playlist Creator

This Python script creates monthly playlists on Spotify and adds the songs you saved in each specific month. It can also create playlists retroactively for previous months.

## Features

- **Monthly Playlists:** Automatically creates a playlist for each month and adds the songs saved in that month.
- **Retroactive Playlists:** Optionally create playlists for past months and add the respective songs saved during those months.
- **Automatic Token Retrieval:** Uses Spotipy's built-in local web server to capture the auth token seamlessly.
- **Reverse Order Addition:** Adds tracks in reverse order to the playlist to maintain the order they were saved.

## Prerequisites

- Python 3.x
- Spotipy
- Spotify Developer Account

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/c-reghiment/spotify_monthly_playlist.git
   cd spotify_monthly_playlist
   ```

2. **Install the required Python libraries:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up Spotify Developer Account:**
   - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications).
   - Create a new app and note down the `Client ID` and `Client Secret`.
   - Set the Redirect URI to `http://localhost:8888/callback`.

4. **Set environment variables:**
   - On Windows:
      ```sh
      setx SPOTIPY_CLIENT_ID "your_client_id"
      setx SPOTIPY_CLIENT_SECRET "your_client_secret"
      setx SPOTIPY_REDIRECT_URI "http://localhost:8888/callback"
      ```
   - On macOS/Linux:
      ```sh
      export SPOTIPY_CLIENT_ID="your_client_id"
      export SPOTIPY_CLIENT_SECRET="your_client_secret"
      export SPOTIPY_REDIRECT_URI="http://localhost:8888/callback"
      ```

## Usage

   1. **Run the script:**
      ```sh
      python spotify_monthly_playlist.py
      ```

   2. **Authenticate with Spotify:**
      - A browser window opens automatically for Spotify login and authorization.
      - If the browser does not open, copy the URL from the terminal into your browser manually.

   3. **Create Playlists:**
      - After authentication, enter how many past months you want to process (enter `0` for the current month only).

## Example

   ```sh
   python spotify_monthly_playlist.py
   ```

   - The script guides you through Spotify authentication.
   - Enter the number of past months to include.
   - Playlists are created (or reused) and populated with the saved songs from each selected month.

## License

   This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

     Contributions are welcome! Please open an issue or submit a pull request.

## Acknowledgments

     - [Spotipy](https://spotipy.readthedocs.io/)
