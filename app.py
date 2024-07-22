import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
import yt_dlp as youtube_dl
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import time
import zipfile
import io
import uuid
import shutil

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

app = Flask(__name__)
CORS(app)


def get_spotify_track_info(track_url):
    results = sp.track(track_url)
    track_info = {
        "name": results["name"],
        "artist": results["artists"][0]["name"],
        "album": results["album"]["name"],
    }
    print(results)
    print("\n\n\n ----------------------------------------------------------\n\n\n")
    return track_info


def get_spotify_playlist_info(playlist_url):
    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    tracks_info = []
    offset = 0
    limit = 100
    while True:
        results = sp.playlist_items(playlist_id, offset=offset, limit=limit)
        for item in results["items"]:
            if item["track"]:
                track = item["track"]
                tracks_info.append(
                    {
                        "name": track["name"],
                        "artist": track["artists"][0]["name"],
                        "album": track["album"]["name"],
                    }
                )
        if len(results["items"]) < limit:
            break
        offset += limit
    return tracks_info


def get_spotify_album_info(album_url):
    album_id = album_url.split("/")[-1].split("?")[0]
    tracks_info = []
    results = sp.album_tracks(album_id)
    album_info = sp.album(album_id)
    album_name = album_info["name"]
    release_date = album_info["release_date"]
    while True:
        for item in results["items"]:
            tracks_info.append(
                {
                    "name": item["name"],
                    "artist": item["artists"][0]["name"],
                    "album": album_name,
                    "release_date": release_date,
                }
            )
        if not results["next"]:
            break
        results = sp.next(results)
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


def download_youtube_video(video_id, output_path, quality, track_info):
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
        "outtmpl": f"{output_path}/{track_info['artist']} - {track_info['name']}.%(ext)s",
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://www.youtube.com/watch?v={video_id}"])


def download_youtube_audio(video_id, output_path, track_info):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{output_path}/{track_info['artist']} - {track_info['name']}.%(ext)s",
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


def download_and_get_file_path(track_info, output_path, quality, download_type):
    query = f"{track_info['artist']} {track_info['name']} {track_info['album']}"
    video_id = search_youtube(query)

    if download_type == "video":
        download_youtube_video(video_id, output_path, quality, track_info)
    else:
        download_youtube_audio(video_id, output_path, track_info)

    expected_file_name = f"{track_info['artist']} - {track_info['name']}"
    downloaded_file = next(
        (
            f
            for f in os.listdir(output_path)
            if os.path.isfile(os.path.join(output_path, f))
            and f.startswith(expected_file_name)
        ),
        None,
    )

    if downloaded_file:
        return os.path.join(output_path, downloaded_file)
    return None


def cleanup_files(file_paths, directory):
    for file_path in file_paths:
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
    try:
        shutil.rmtree(directory)
    except Exception as e:
        print(f"Error deleting directory {directory}: {e}")


@app.route("/download", methods=["POST"])
def download():
    data = request.json
    url = data.get("url")
    quality = data.get("quality", "1080px")
    download_type = data.get("type", "video")

    try:
        unique_dir = f"temp_downloads_{uuid.uuid4()}"
        os.makedirs(unique_dir)

        if "playlist" in url:
            tracks_info = get_spotify_playlist_info(url)
        elif "album" in url:
            tracks_info = get_spotify_album_info(url)
        else:
            tracks_info = [get_spotify_track_info(url)]

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            file_paths = []
            for track_info in tracks_info:
                file_path = download_and_get_file_path(
                    track_info, unique_dir, quality, download_type
                )
                if file_path:
                    file_name = os.path.basename(file_path)
                    zip_file.write(file_path, file_name)
                    file_paths.append(file_path)
                time.sleep(5)  # Pause before downloading the next track

        zip_buffer.seek(0)

        response = send_file(
            zip_buffer,
            as_attachment=True,
            download_name="spotify_download.zip",
            mimetype="application/zip",
        )

        # Cleanup files after sending the response
        cleanup_files(file_paths, unique_dir)

        return response

    except spotipy.exceptions.SpotifyException as e:
        cleanup_files([], unique_dir)
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        cleanup_files([], unique_dir)
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
