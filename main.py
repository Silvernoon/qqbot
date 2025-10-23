#!/usr/bin/python3

from flask import Flask, request, jsonify
import os
import time
import requests
import qqapi
import openai

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def handle_webhook():
    # 验证签名
    signature = request.headers.get("X-Signature-Ed25519", "")
    timestamp = request.headers.get("X-Signature-Timestamp", "")

    if not qqapi.verify(signature, timestamp, request.get_data().decode()):
        return 400

    body = request.json
    d = body.get("d")

    match body.get("op"):
        case 0:
            # print(body)
            content = d.get("content")
            # print(f"收到消息：{content}")

            event_type = body["t"]

            match event_type:
                case "GROUP_AT_MESSAGE_CREATE":
                    qqapi.group_reply(d["group_openid"], event_type, d["id"])
                case "C2C_MESSAGE_CREATE":
                    qqapi.users_dm_reply(d["author"]["id"], event_type, d["id"])
            return jsonify({}), 200
        case 13:
            outsign = qqapi.sign(d["event_ts"] + d["plain_token"])

            return jsonify(
                {"plain_token": d["plain_token"], "signature": outsign.hex()}
            ), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
