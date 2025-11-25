import requests
import yt_dlp as youtube_dl
import os

def get_youtube_video_info(url) -> dict:
    ydl_opts = {
        'quiet': True,  # Suppress output for efficiency
        'no_warnings': False,
        'noplaylist': True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:  # type: ignore
        info = ydl.extract_info(url, download=False)
        formats = info.get('formats', None)

        if formats is None:
            raise ValueError("No formats found for the given YouTube URL")

        metadata = {
            'title': info.get('title'),
            'channel': info.get('channel'),
            'thumbnail': info.get('thumbnail'),
        }
        
        combined_details = {}
        for f in formats:
            if f.get('ext') == 'mp4' and f.get('acodec') != 'none':
                height = f.get('height')
                if height:
                    res = f"{height}p"
                    id = f.get('format_id')
                    combined_details[res] = {
                        "format_id": id if id else "Unknown"
                    }

        video_details = {}
        for f in formats:
            if f.get('ext') == 'mp4' and f.get('vcodec') != 'none':
                height = f.get('height')
                if height:
                    res = f"{height}p"
                    size = f.get('filesize') or f.get('filesize_approx')
                    id = f.get('format_id')

                    video_details[res] = {
                        "filesize": round(size / (1024 * 1024), 1) if size else "Unknown",
                        "format_id": id if id else "Unknown",
                    }

        audio_bitrates = {}
        for f in formats:
            if f.get('ext') == 'm4a' and f.get('acodec') != 'none':
                abr = f.get('abr')
                if abr:
                    abr = f"{int(abr)}k"
                    size = f.get('filesize') or f.get('filesize_approx')
                    id = f.get('format_id')

                    audio_bitrates[abr] = {
                        "filesize": round(size / (1024 * 1024), 1) if size else "Unknown",
                        "format_id": id if id else "Unknown"
                    }

        return {
            'metadata': metadata,
            'combined_details': sorted(combined_details.items(), key=lambda x: int(x[0][:-1]), reverse=True),
            'video_details': sorted(video_details.items(), key=lambda x: int(x[0][:-1]), reverse=True),
            'audio_bitrates': sorted(audio_bitrates.items(), key=lambda x: int(x[0][:-1]), reverse=True),
        }
    
def download_preview(url):
    # Extract video ID from the URL path (assuming format like /vi/{id}/...)
    try:
        id = url.split("/vi/")[1].split("/")[0]
    except IndexError:
        # Fallback if URL doesn't match expected format
        id = "unknown"
    
    # Extract file extension from the URL
    filename = url.split('/')[-1]
    ext = filename.split('.')[-1] if '.' in filename else 'jpg'
    
    # Ensure the downloads directory exists
    os.makedirs("downloads", exist_ok=True)
    
    response = requests.get(url)
    if response.status_code == 200:
        filepath = os.path.join("downloads", f"preview_{id}.{ext}")
        with open(filepath, "wb") as f:
            f.write(response.content)
        # print(f"Preview image downloaded as preview_{id}.{ext}")
        return filepath
    else:
        # print("Failed to download preview image")
        return None
    
def download_video(url, format_id):
    ydl_opts = {
        'quiet': True,  # Suppress output for efficiency
        'format': format_id,
        'noplaylist': True,
        'outtmpl': os.path.join("downloads", f"%(title)s_{format_id}.%(ext)s"),
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:  # type: ignore
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)