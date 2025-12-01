import pyktok as pyk
import os

def get_tiktok_metadata(tiktok_url: str) -> dict:
    tt_json = pyk.alt_get_tiktok_json(f'{tiktok_url}?is_copy_url=1&is_from_webapp=v1')
    assert isinstance(tt_json, dict)

    share_meta = tt_json['__DEFAULT_SCOPE__']['webapp.video-detail']['shareMeta']
    return share_meta

def _parse_video_name(tiktok_url: str) -> str:
    tiktok_urls = ["vm.tiktok.com", "vt.tiktok.com"]

    if any(url in tiktok_url for url in tiktok_urls):
        parts = parts = tiktok_url.replace("https://vm.tiktok.com/", "").rstrip("/") if "vm.tiktok.com" in tiktok_url else tiktok_url.replace("https://vt.tiktok.com/", "").rstrip("/")
        if tiktok_url.endswith("/"):
            return f"{parts}_.mp4"
        else:
            return f"{parts}.mp4"
    else:
        import re
        match = re.search(r'@([^/]+)/video/(\d+)', tiktok_url)
        if match:
            username = match.group(1)
            video_id = match.group(2)
            return f"@{username}_video_{video_id}.mp4"
        else:
            raise ValueError("Invalid TikTok URL format")

def download_tiktok_video(tiktok_url: str) -> str:    
    os.makedirs("downloads", exist_ok=True)
    os.chdir("downloads")
    
    pyk.save_tiktok(tiktok_url, save_video=True)

    os.chdir("..")

    video_path = os.path.join("downloads", _parse_video_name(tiktok_url))

    return video_path