import os
import random
import re
from googleapiclient.discovery import build

def get_random_video_from_playlist(playlist_url):
    """
    Takes a YouTube playlist link, grabs the videos, 
    and returns a random video's ID, title, and thumbnail.
    """
    api_key = os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        return {"error": "Missing YOUTUBE_API_KEY environment variable."}

    try:
        # 1. Extract Playlist ID using Regex
        # Handles formats: youtube.com/playlist?list=ID or youtube.com/watch?v=ID&list=ID
        playlist_id_match = re.search(r"list=([a-zA-Z0-9_-]+)", playlist_url)
        if not playlist_id_match:
            return {"error": "Invalid YouTube playlist link!"}
        
        playlist_id = playlist_id_match.group(1)

        # 2. Build the YouTube Service
        youtube = build('youtube', 'v3', developerKey=api_key)

        # 3. Fetch Playlist Items
        # Note: This fetches the first 50 items. You can use pagination for larger playlists.
        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50
        )
        response = request.execute()
        items = response.get('items', [])

        if not items:
            return {"error": "This playlist is empty or private!"}

        # 4. Pick a random video
        random_item = random.choice(items)
        snippet = random_item['snippet']
        video_id = random_item['contentDetails']['videoId']

        # 5. Return data in a format similar to your Spotify utils
        return {
            'name': snippet['title'],
            'artist': snippet['videoOwnerChannelTitle'] if 'videoOwnerChannelTitle' in snippet else "Unknown Artist",
            'video_id': video_id, # This replaces preview_url
            'cover_art': snippet['thumbnails']['high']['url'] if 'thumbnails' in snippet else None
        }

    except Exception as e:
        print(f"YouTube Fetch Error: {e}")
        return {"error": f"YouTube API Error: {str(e)}"}