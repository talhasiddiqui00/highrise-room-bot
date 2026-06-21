import os
import yt_dlp
from flask import Flask, Response, request

app = Flask(__name__)

# Configuration for yt-dlp to bypass bot detection
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'cookiefile': 'cookies.txt',  # Requires cookies.txt in the same folder
    'extractor_args': {
        'youtube': {
            'player_client': ['web_safari'],
        }
    },
    'quiet': False,
    'no_warnings': False,
}

@app.route('/room_music')
def stream_music():
    query = request.args.get('q', 'lofi hip hop radio')
    
    # Use yt-dlp to fetch the streaming URL
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if 'entries' in info:
                video_url = info['entries'][0]['url']
            else:
                video_url = info['url']
        except Exception as e:
            return f"Error extracting audio: {str(e)}", 500

    # Return the stream URL so the room player can connect
    return Response(video_url, mimetype='text/plain')

@app.route('/')
def index():
    return "Bot Music Engine is Online", 200

if __name__ == "__main__":
    # Render assigns the port via the PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
