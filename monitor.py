import time
import signal
import sys

import schedule

from datetime import datetime, timezone, timedelta

from config import TIKTOK_USERNAME, CHECK_INTERVAL_MINUTES
from tiktok_api import search_user, get_user_videos
from db import init_db, is_new_video, add_video
from notifier import send_wechat

running = True


def signal_handler(sig, frame):
    global running
    print("\nShutting down...")
    running = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def check_new_videos(username: str):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking @{username}...")
    try:
        videos = get_user_videos(username, count=10)
    except Exception as e:
        print(f"  [Error] API request failed: {e}")
        return
    if not videos:
        print("  No videos found or API error")
        return

    new_count = 0
    for v in videos:
        if is_new_video(v["video_id"]):
            new_count += 1
            add_video(v["video_id"], username, v["title"])

    # Always send the latest video info
    latest = videos[0]
    publish_time = datetime.fromtimestamp(latest["create_time"], tz=timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
    send_wechat(
        title=f"@{username} 最新视频",
        content=(
            f"> **{latest['title'][:80]}**\n"
            f"> 发布时间: {publish_time}\n"
            f"> 播放: {latest['play_count']} | 点赞: {latest['digg_count']} | 评论: {latest['comment_count']}\n"
            f"> [观看视频]({latest['url']})"
        ),
    )

    print(f"  Found {len(videos)} videos, {new_count} new")


def main():
    init_db()

    # First run: record existing videos and send latest video info
    print(f"First run: recording existing videos for @{TIKTOK_USERNAME}...")
    videos = get_user_videos(TIKTOK_USERNAME, count=10)
    if not videos:
        print(f"[Warning] No videos found for @{TIKTOK_USERNAME}. Please check the username.")
    for v in videos:
        if is_new_video(v["video_id"]):
            add_video(v["video_id"], TIKTOK_USERNAME, v["title"])
    print(f"Recorded {len(videos)} existing videos.")

    # Send latest video notification on startup
    if videos:
        latest = videos[0]
        publish_time = datetime.fromtimestamp(latest["create_time"], tz=timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
        send_wechat(
            title=f"@{TIKTOK_USERNAME} 最新视频",
            content=(
                f"> **{latest['title'][:80]}**\n"
                f"> 发布时间: {publish_time}\n"
                f"> 播放: {latest['play_count']} | 点赞: {latest['digg_count']} | 评论: {latest['comment_count']}\n"
                f"> [观看视频]({latest['url']})"
            ),
        )
    print("Monitoring started.\n")

    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_new_videos, TIKTOK_USERNAME)

    while running:
        schedule.run_pending()
        time.sleep(1)

    print("Exited.")


if __name__ == "__main__":
    main()
