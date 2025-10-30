from cryptography.hazmat.primitives.asymmetric import ed25519
import requests
import time
import os

BASE_URL = "https://api.sgroup.qq.com"
AUTH_URL = "https://bots.qq.com/app/getAppAccessToken"

BOT_SECRET = os.environ["BOT_SECRET"]
APP_ID = os.environ["APP_ID"]

PRI_KEY = ed25519.Ed25519PrivateKey.from_private_bytes(BOT_SECRET.encode())
PUB_KEY = PRI_KEY.public_key()

lastt = 0
access_token = ""


def get_auth():
    global lastt
    global access_token
    response = requests.post(
        AUTH_URL,
        headers={"Content-Type": "application/json"},
        json={"appId": APP_ID, "clientSecret": BOT_SECRET},
    )
    if response.status_code == 200:
        ret = response.json()
        lastt = time.time() + float(ret["expires_in"])
        access_token = ret["access_token"]


def get_auth_headers():
    global access_token, lastt
    if time.time() > lastt:
        get_auth()
    return {
        "Authorization": f"QQBot {access_token}",
        "Content-Type": "application/json",
    }


def sign(data: str):
    return PRI_KEY.sign(data.encode())


def verify(signature: str, timestamp: str, data: str) -> bool:
    sig = bytes.fromhex(signature)
    if sig[63] & 224 != 0:
        print("签名无效")
        return False

    msg: str = timestamp + data
    try:
        PUB_KEY.verify(sig, msg.encode())
    except Exception as e:
        print(f"签名验证失败, {e}")
        return False

    return True


def users_dm_reply(openid, event_id, msg_id, content="何意味"):
    response = requests.post(
        f"{BASE_URL}/v2/users/{openid}/messages",
        headers=get_auth_headers(),
        json={
            "content": content,
            "msg_type": 0,
            "event_id": event_id,
            "msg_id": msg_id,
        },
    )
    return response


def group_reply(group_openid, event_id, msg_id, content="何意味"):
    response = requests.post(
        f"{BASE_URL}/v2/groups/{group_openid}/messages",
        headers=get_auth_headers(),
        json={
            "content": content,
            "msg_type": 0,
            "event_id": event_id,
            "msg_id": msg_id,
        },
    )
    return response
