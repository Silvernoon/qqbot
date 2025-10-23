from typing import Dict, TypedDict
import requests
import os


class user(TypedDict):
    qq_userid: str
    api_key: str


keys: Dict[str, user] = dict()


def load():
    global keys
    with open("keys", "r", encoding="utf-8") as file:
        for line in file:
            datas = line.split(" ")
            keys[datas[0]] = {"qq_userid": datas[0], "api_key": datas[1]}


def get_key(id: str) -> str:
    return keys[id]["api_key"]


def chat_with_model(token: str, content: str):
    url = "http://localhost:8070/api/chat/completions"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "model": "deepseek-v3-1-terminus",
        "messages": [{"role": "user", "content": content}],
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()
