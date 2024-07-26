import os
import time
import subprocess
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Get API key from environment variable
API_KEY = os.getenv('YOUTUBE_API_KEY')
CHANNELS = {
    "Channel_3": "UCirZPTc9IoKM_DsA9aKbc4g",
    "thairath": "UCrFDdD-EE05N7gjwZho2wqw",
    "glaibaan": "UCx2PGrMyLVyUl9rte_JqWlw",
    # Add more channels as needed
}

# Directory to store the output files
OUTPUT_DIR = "video_segments"

def get_live_video_id(channel_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    try:
        request = youtube.search().list(
            part='snippet',
            channelId=channel_id,
            eventType='live',
            type='video'
        )
        response = request.execute()
        if response['items']:
            return response['items'][0]['id']['videoId']
    except HttpError as e:
        if e.resp.status == 429:
            print("Hit rate limit. Sleeping for 5 minutes.")
            time.sleep(300)
        else:
            print(f"An error occurred: {e}")
    return None

def create_m3u8_from_youtube(video_id, channel_name):
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_path = os.path.join(OUTPUT_DIR, channel_name)
    os.makedirs(output_path, exist_ok=True)
    command = (
        f"streamlink -O {url} best | "
        f"ffmpeg -i - -c copy -f hls -hls_time 10 "
        f"-hls_list_size 0 -hls_segment_filename '{output_path}/segment_%03d.ts' {output_path}/{channel_name}.m3u8"
    )
    process = subprocess.Popen(command, shell=True)
    return process

def main():
    while True:
        for channel_name, channel_id in CHANNELS.items():
            video_id = get_live_video_id(channel_id)
            if video_id:
                print(f'Starting to stream live video from channel {channel_name}: {video_id}')
                process = create_m3u8_from_youtube(video_id, channel_name)
                while process.poll() is None:
                    time.sleep(10)  # Sleep for 10 seconds before checking again
                # Display the URL of the created m3u8 file
                m3u8_url = f"https://9putt.github.io/plusm3u8/{OUTPUT_DIR}/{channel_name}/{channel_name}.m3u8"
                print(f'm3u8 URL: {m3u8_url}')
            else:
                print(f"No live video found for channel: {channel_name}")
                time.sleep(300)  # Sleep for 5 minutes if no live video found

if __name__ == "__main__":
    main()
