#!/usr/bin/python3

from typing import Dict
from flask import Flask, request, jsonify
import sys
import logging
import qqapi
import openai
from collections import deque


app = Flask(__name__)
# openai.load()

last_msg_ids = deque[str](maxlen=20)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

chats: Dict[str, openai.ResponseChat] = {}


@app.route("/webhook", methods=["POST"])
def handle_webhook():
    # 验证签名
    signature = request.headers.get("X-Signature-Ed25519", "")
    timestamp = request.headers.get("X-Signature-Timestamp", "")

    if not qqapi.verify(signature, timestamp, request.get_data().decode()):
        return jsonify({"error": "签名错误"}), 400

    body = request.json
    d = body.get("d")

    match body.get("op"):
        case 0:
            # print(body)
            content = d.get("content")
            if type(content) is not str:
                print("无效内容")
                return jsonify({"error": "无效内容"}), 400

            # print(f"收到消息：{content}")

            event_type = body["t"]
            author_id = d["author"]["id"]
            msg_id = d["id"]

            global last_msg_ids
            if msg_id in last_msg_ids:
                print("重复对话")
                return jsonify({"error": "重复对话"}), 400
            else:
                last_msg_ids.append(msg_id)

            global chats

            match event_type:
                case "GROUP_AT_MESSAGE_CREATE":
                    group_id = d["group_openid"]
                    if not chats.get(group_id):
                        chats[group_id] = openai.ResponseChat()

                    qqapi.group_reply(
                        group_id,
                        event_type,
                        msg_id,
                        chats[group_id].try_chat_with_cache(content, author_id),
                    )
                case "C2C_MESSAGE_CREATE":
                    if not chats.get(author_id):
                        chats[author_id] = openai.ResponseChat()

                    qqapi.users_dm_reply(
                        author_id,
                        event_type,
                        msg_id,
                        chats[author_id].try_chat_with_cache(content, author_id),
                    )
            return jsonify({}), 200
        case 13:
            outsign = qqapi.sign(d["event_ts"] + d["plain_token"])
            return jsonify(
                {"plain_token": d["plain_token"], "signature": outsign.hex()}
            ), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
