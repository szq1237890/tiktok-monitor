import httpx
from config import WECHAT_WEBHOOK_URL


def send_wechat(title: str, content: str):
    if not WECHAT_WEBHOOK_URL:
        print("[Warn] WECHAT_WEBHOOK_URL not configured, skipping notification")
        return

    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"### {title}\n{content}",
        },
    }
    resp = httpx.post(WECHAT_WEBHOOK_URL, json=payload)
    result = resp.json()
    if result.get("errcode") != 0:
        print(f"[Error] WeChat webhook: {result}")
    else:
        print(f"[OK] Notification sent: {title}")
