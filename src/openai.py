from typing import Dict, TypedDict
import requests
import time
import os


# ------------------------


class user(TypedDict):
    name: str


users: Dict[str, user] = dict()


def load():
    global users
    with open("keys", "r", encoding="utf-8") as file:
        for line in file:
            datas = line.split(" ")
            users[datas[0]] = {"name": datas[1]}


# -----------------------------------------

BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
KEY = os.environ["API_KEY"]
HEADER = {
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
}
ENDPOINT = os.environ["AI_ENDPOINT"]

PROMPT = "你是qq群的聊天ai，你的回复要简短，输出格式不要带markdown"


class ContextChat:
    def __init__(self) -> None:
        response = requests.post(
            f"{BASE_URL}/context/create",
            headers=HEADER,
            json={
                "model": ENDPOINT,
                "caching": {"type": "enabled"},
                "thinking": {"type": "disabled"},
                "messages": [
                    {
                        "role": "system",
                        "content": PROMPT,
                    }
                ],
                "ttl": 3600,
                "mode": "session",
                "truncation_strategy": {
                    "type": "only_second",
                },
            },
        )
        response = response.json()
        self.context_id = response["context_id"]

    def chat(self, content: str) -> str:
        return requests.post(
            f"{BASE_URL}/chat/completions",
            headers=HEADER,
            json={
                "context_id": self.context_id,
                "model": ENDPOINT,
                "messages": [{"role": "user", "content": content}],
            },
        ).json()["choices"][0]["message"]["content"]


class ResponseChat:
    def __init__(self) -> None:
        self.previous_response_id: str = ""
        self.last_timestamp = 0
        self.data = {
            "model": "deepseek-v3-1-terminus",
            "caching": {"type": "enabled"},
            "thinking": {"type": "disabled"},
            "expire_at": int(time.time()) + 3600,
        }

        self.chat_with_cache(
            [
                {
                    "role": "system",
                    "content": PROMPT,
                }
            ]
        )

    def chat_with_cache(self, content) -> str:
        if self.previous_response_id != "" and self.last_timestamp > time.time():
            self.data["previous_response_id"] = self.previous_response_id

        self.data["input"] = content

        response = requests.post(
            f"{BASE_URL}/responses",
            headers=HEADER,
            json=self.data,
        ).json()

        self.previous_response_id = response["id"]
        self.last_timestamp = response["expire_at"]

        return response["output"][0]["content"][0]["text"]

    def delete_cache(self, response_id=None):
        if response_id is None:
            response_id = self.previous_response_id
        return requests.delete(f"{BASE_URL}/responses/{response_id}")
