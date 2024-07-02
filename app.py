import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
import yt_dlp as youtube_dl
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
# Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# YouTube API credentials
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Initialize Spotify client
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET
    )
)

# Initialize YouTube client
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


def get_spotify_track_info(track_url):
    results = sp.track(track_url)
    track_info = {"name": results["name"], "artist": results["artists"][0]["name"]}
    return track_info


def get_spotify_playlist_info(playlist_url):
    results = sp.playlist_tracks(playlist_url)
    tracks_info = []
    for item in results["items"]:
        track = item["track"]
        tracks_info.append(
            {"name": track["name"], "artist": track["artists"][0]["name"]}
        )
    return tracks_info


def get_spotify_album_info(album_url):
    results = sp.album_tracks(album_url)
    tracks_info = []
    for item in results["items"]:
        tracks_info.append({"name": item["name"], "artist": item["artists"][0]["name"]})
    return tracks_info


def search_youtube(query):
    request = youtube.search().list(
        q=f"{query} official full video song",
        part="snippet",
        maxResults=1,
        type="video",
    )
    response = request.execute()
    return response["items"][0]["id"]["videoId"]


def download_youtube_video(video_id, output_path, quality):
    quality_mapping = {
        "Highest": "bestvideo+bestaudio/best",
        "1080px": "bestvideo[height<=1080]+bestaudio/best",
        "720px": "bestvideo[height<=720]+bestaudio/best",
        "480px": "bestvideo[height<=480]+bestaudio/best",
        "360px": "bestvideo[height<=360]+bestaudio/best",
        "Lowest": "worstvideo+bestaudio/best",
    }
    ydl_format = quality_mapping.get(quality, "bestvideo+bestaudio/best")

    ydl_opts = {
        "format": ydl_format,
        "outtmpl": f"{output_path}/%(title)s.%(ext)s",
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://www.youtube.com/watch?v={video_id}"])


def download_youtube_audio(video_id, output_path):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{output_path}/%(title)s.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://www.youtube.com/watch?v={video_id}"])


def download_spotify_track(track_url, output_path, quality, download_type):
    track_info = get_spotify_track_info(track_url)
    query = f"{track_info['artist']} {track_info['name']}"
    video_id = search_youtube(query)
    if download_type == "video":
        download_youtube_video(video_id, output_path, quality)
    else:
        download_youtube_audio(video_id, output_path)


def download_spotify_playlist(playlist_url, output_path, quality, download_type):
    tracks_info = get_spotify_playlist_info(playlist_url)
    for track_info in tracks_info:
        query = f"{track_info['artist']} {track_info['name']}"
        video_id = search_youtube(query)
        if download_type == "video":
            download_youtube_video(video_id, output_path, quality)
        else:
            download_youtube_audio(video_id, output_path)


def download_spotify_album(album_url, output_path, quality, download_type):
    tracks_info = get_spotify_album_info(album_url)
    for track_info in tracks_info:
        query = f"{track_info['artist']} {track_info['name']}"
        video_id = search_youtube(query)
        if download_type == "video":
            download_youtube_video(video_id, output_path, quality)
        else:
            download_youtube_audio(video_id, output_path)


app = Flask(__name__)
CORS(app)


@app.route("/download", methods=["POST"])
def download():
    data = request.json
    url = data.get("url")
    output_path = data.get("output_path")
    quality = data.get("quality", "1080px")
    download_type = data.get("type", "video")
    try:
        if "playlist" in url:
            download_spotify_playlist(url, output_path, quality, download_type)
        elif "album" in url:
            download_spotify_album(url, output_path, quality, download_type)
        else:
            download_spotify_track(url, output_path, quality, download_type)
        return jsonify({"status": "success"})
    except spotipy.exceptions.SpotifyException as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
