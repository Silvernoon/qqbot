from typing import Dict, TypedDict
import requests
import os

KEY = os.environ["API_KEY"]


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
class Chat:
    def __init__(self) -> None:
        self.previous_response_id: str
        self.data = {
            "model": "deepseek-v3-1-terminus",
            "caching": {"type": "enabled"},
            "thinking": {"type": "disabled"},
        }

    def chat_with_cache(self, content: str) -> str:
        if self.previous_response_id:
            self.data["previous_response_id"] = self.previous_response_id
            self.data["input"] = content

        response = requests.post(
            "https://ark.cn-beijing.volces.com/api/v3/responses",
            headers={
                "Authorization": f"Bearer {KEY}",
                "Content-Type": "application/json",
            },
            json=self.data,
        ).json()

        self.previous_response_id = response["id"]

        return response["output"][0]["content"]["text"]

    def delete_cache(self, response_id=None):
        if response_id is None:
            response_id = self.previous_response_id
        return requests.delete(
            f"https://ark.cn-beijing.volces.com/api/v3/responses/{response_id}"
        )
