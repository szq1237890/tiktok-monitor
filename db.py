import sqlite3
from datetime import datetime

DB_PATH = "tiktok_monitor.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                author TEXT,
                title TEXT,
                created_at TEXT
            )
        """)
        conn.commit()


def is_new_video(video_id: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM videos WHERE video_id = ?", (video_id,)
        ).fetchone()
        return row is None


def add_video(video_id: str, author: str, title: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO videos (video_id, author, title, created_at) VALUES (?, ?, ?, ?)",
            (video_id, author, title, datetime.now().isoformat()),
        )
        conn.commit()
