from googleapiclient.discovery import build
from dotenv import load_dotenv
load_dotenv()

youtube = build('youtube', 'v3', developerKey='YOUTUBE_API_KEY')

# Fetch the details of a specific video
video_id = '9AitwLeeUyA'  # Replace with the ID of the video you want to fetch
request = youtube.videos().list(part='snippet,statistics', id=video_id)
response = request.execute()

print(response)