import httpx
from config import RAPIDAPI_KEY, RAPIDAPI_HOST, RAPIDAPI_BASE_URL

HEADERS = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST,
    "Content-Type": "application/json",
}


def search_user(keyword: str) -> dict | None:
    resp = httpx.get(
        f"{RAPIDAPI_BASE_URL}/user/search",
        headers=HEADERS,
        params={"keywords": keyword, "count": 10, "cursor": 0},
    )
    data = resp.json()
    if data.get("code") != 0:
        print(f"[API Error] search_user: {data.get('msg')}")
        return None

    for item in data["data"].get("user_list", []):
        user = item["user"]
        if user["uniqueId"].lower() == keyword.lower():
            return {
                "uid": user["id"],
                "unique_id": user["uniqueId"],
                "nickname": user["nickname"],
                "sec_uid": user["secUid"],
            }
    return None


def get_user_videos(unique_id: str, count: int = 10) -> list[dict]:
    resp = httpx.get(
        f"{RAPIDAPI_BASE_URL}/user/posts",
        headers=HEADERS,
        params={"unique_id": unique_id, "count": count, "cursor": 0},
    )
    data = resp.json()
    if data.get("code") != 0:
        print(f"[API Error] get_user_videos: code={data.get('code')}, msg={data.get('msg')}")
        return []

    videos = []
    for v in data["data"].get("videos", []):
        videos.append({
            "video_id": v["aweme_id"],
            "title": v.get("title", ""),
            "create_time": v.get("create_time", 0),
            "play_count": v.get("play_count", 0),
            "digg_count": v.get("digg_count", 0),
            "comment_count": v.get("comment_count", 0),
            "url": f"https://www.tiktok.com/@{unique_id}/video/{v['video_id']}",
            "cover": v.get("cover", ""),
        })
    print(f"[Debug] API returned {len(videos)} videos for @{unique_id}")
    return videos
