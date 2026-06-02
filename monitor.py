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


def is_active_time():
    """检查当前时间是否在活跃时间段（20:00-23:00）"""
    now = datetime.now()
    return 20 <= now.hour < 23


def wait_for_active_time():
    """等待到下一个活跃时间段"""
    now = datetime.now()
    if now.hour < 20:
        # 等待到今天 20:00
        target = now.replace(hour=20, minute=0, second=0, microsecond=0)
    else:
        # 等待到明天 20:00
        target = (now + timedelta(days=1)).replace(hour=20, minute=0, second=0, microsecond=0)

    wait_seconds = (target - now).total_seconds()
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] 非活跃时间段，等待到 {target.strftime('%Y-%m-%d %H:%M')}...")
    time.sleep(wait_seconds)


def main():
    init_db()

    # 首次运行：记录现有视频
    print(f"首次运行：记录 @{TIKTOK_USERNAME} 的现有视频...")
    videos = get_user_videos(TIKTOK_USERNAME, count=10)
    if not videos:
        print(f"[警告] 未找到 @{TIKTOK_USERNAME} 的视频，请检查用户名。")
    for v in videos:
        if is_new_video(v["video_id"]):
            add_video(v["video_id"], TIKTOK_USERNAME, v["title"])
    print(f"已记录 {len(videos)} 个视频。")

    print(f"监控已启动，活跃时间：每天 20:00-23:00，每 {CHECK_INTERVAL_MINUTES} 分钟检查一次。\n")

    while running:
        if is_active_time():
            # 在活跃时间段内，执行检查
            check_new_videos(TIKTOK_USERNAME)

            # 等待下一次检查
            for _ in range(CHECK_INTERVAL_MINUTES * 60):
                if not running:
                    break
                time.sleep(1)
        else:
            # 不在活跃时间段，等待
            wait_for_active_time()

    print("已退出。")


if __name__ == "__main__":
    main()
