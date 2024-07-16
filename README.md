# Spotify Monthly Playlist Creator

This Python script creates monthly playlists on Spotify and adds the songs you saved in each specific month. It can also create playlists retroactively for previous months.

## Features

- **Monthly Playlists:** Automatically creates a playlist for each month and adds the songs saved in that month.
- **Retroactive Playlists:** Optionally create playlists for past months and add the respective songs saved during those months.
- **Automatic Token Retrieval:** Uses Flask to handle Spotify authentication and capture the token seamlessly.
- **Reverse Order Addition:** Adds tracks in reverse order to the playlist to maintain the order they were saved.

## Prerequisites

- Python 3.x
- Flask
- Spotipy
- Spotify Developer Account

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/c-reghiment/spotify_monthly_playlist.git
   cd spotify-monthly-playlist-creator

2. **Install the required Python libraries:**
        ```sh
        pip install spotipy Flask
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
        python spotify_monthly_playlist_creator.py
        ```

     2. **Authenticate with Spotify:**
        - The script will open a browser window to prompt for Spotify login and authorization.
        - After logging in, copy the URL you are redirected to and paste it back into the terminal.

     3. **Create Playlists:**
        - Enter the number of past months you want to create playlists for (e.g., enter `0` to create only the current month's playlist).

## Example

     ```sh
     python spotify_monthly_playlist_creator.py
     ```

     - The script will prompt you to authenticate with Spotify.
     - After authentication, enter the number of past months you want to create playlists for.
     - The script will create the playlists and add the saved songs for each specified month.

     ## License

     This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

     Contributions are welcome! Please open an issue or submit a pull request.

     ## Acknowledgments

     - [Spotipy](https://spotipy.readthedocs.io/en/2.19.0/#)
     - [Flask](https://flask.palletsprojects.com/en/2.0.x/)
