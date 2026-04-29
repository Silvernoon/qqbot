from abc import abstractmethod
from typing import Dict, TypedDict, Optional

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


PROMPT = """
你是qq群的聊天ai，你的回复要简短，输出格式不要带markdown. 
你会收到多名User的消息，消息头部带有User的id。有时id后面会附带括号，括号内是User的昵称，在必要情况使用昵称称呼User。
如："ABCDEFGHIGKLMNOPQRSTUVWXYZABCDEF(Alice):你好"
当你收到"何意味"时，回复"何意味"或者"何意味啊"
"""


class LLMHander:
    def __init__(self) -> None:
        self.base_url: str
        self.system_prompt = PROMPT

    @abstractmethod
    def chat(self, input) -> str:
        pass

    def get_models_list(self):
        return []
