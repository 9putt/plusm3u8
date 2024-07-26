import os
from googleapiclient.discovery import build
import time
import subprocess

# Get API key from environment variable
API_KEY = os.getenv('YOUTUBE_API_KEY')
CHANNELS = {
    "Channel_1": "CHANNEL_ID_1",
    "Channel_2": "CHANNEL_ID_2",
    "Channel_3": "CHANNEL_ID_3",
    # Add more channels as needed
}

def get_live_video_id(channel_id):
    # Initialize the YouTube API client
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    # Check for live broadcast on the specified channel
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        eventType='live',
        type='video'
    )
    response = request.execute()

    # If there is a live broadcast, return the live video ID
    if response['items']:
        return response['items'][0]['id']['videoId']
    else:
        return None

def create_m3u8_from_youtube(video_id, channel_name):
    # Construct the YouTube video URL
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    # Command to use Streamlink and FFmpeg to create an m3u8 file
    command = (
        f"streamlink -O {url} best | "
        f"ffmpeg -i - -c copy -f hls -hls_time 10 "
        f"-hls_list_size 0 -hls_segment_filename '{channel_name}/segment_%03d.ts' {channel_name}/{channel_name}.m3u8"
    )
    
    # Run the command in the shell
    subprocess.Popen(command, shell=True)

def main():
    while True:
        for channel_name, channel_id in CHANNELS.items():
            # Get the live video ID for the specified channel
            video_id = get_live_video_id(channel_id)
            if video_id:
                # Create the output directory if it doesn't exist
                subprocess.run(f"mkdir -p {channel_name}", shell=True)
                
                # Print the channel and video ID
                print(f'Starting to stream live video from channel {channel_name}: {video_id}')
                
                # Create the m3u8 file from the live video
                create_m3u8_from_youtube(video_id, channel_name)
            else:
                print(f"No live video found for channel: {channel_name}")
        
        # Wait for a certain period before checking again (e.g., 5 minutes)
        time.sleep(300)

if __name__ == "__main__":
    main()
