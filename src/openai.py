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

PROMPT = """
你是qq群的聊天ai，你的回复要简短，输出格式不要带markdown. 
你会收到多名User的消息，消息头部带有User的id。有时id后面会附带括号，括号内是User的昵称，在必要情况使用昵称称呼User。
如："ABCDEFGHIGKLMNOPQRSTUVWXYZABCDEF(Alice):你好"
当你收到"何意味"时，回复"何意味"或者"何意味啊"
"""


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
        self.reset()

    def reset(self):
        msg = [
            {
                "role": "system",
                "content": PROMPT,
            }
        ]
        self.chat_response(msg)

        # debug
        print("reset")

    def try_chat_with_cache(self, content, userid) -> str:
        data = {}
        if self.previous_response_id:
            if self.last_timestamp > time.time():
                data["previous_response_id"] = self.previous_response_id
            else:
                self.reset()

        global users
        if userid in users.keys():
            userid += users[userid].get("name")
        content = userid + ":" + content

        # debug
        print(content)

        rep = self.chat_response(content, data)

        return rep["output"][0]["content"][0]["text"]

    def chat_response(self, input, data: dict = {}, ttl: int = 3600):
        rep = requests.post(
            f"{BASE_URL}/responses",
            headers=HEADER,
            json={
                "model": ENDPOINT,
                "caching": {"type": "enabled"},
                "thinking": {"type": "disabled"},
                "input": input,
                "expire_at": int(time.time()) + ttl,
                **data,
            },
        ).json()

        print(rep)

        self.previous_response_id = rep.get("id")
        self.last_timestamp = rep["expire_at"]

        return rep

    def delete_cache(self, response_id=None):
        if response_id is None:
            response_id = self.previous_response_id
        return requests.delete(f"{BASE_URL}/responses/{response_id}")
