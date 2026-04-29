#!/usr/bin/python3

from typing import Dict
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sys
import logging
import qqapi
import openai
import llm.ark_llm as ark
from collections import deque

last_msg_ids = deque[str](maxlen=20)
chats: Dict[str, ark.ArkResponseChat] = {}

# logger
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = FastAPI()


@app.post("/webhook")
async def handle_webhook(request: Request):
    # 验证签名
    signature = request.headers.get("X-Signature-Ed25519", "")
    timestamp = request.headers.get("X-Signature-Timestamp", "")

    raw_body = await request.body()
    if not qqapi.verify(signature, timestamp, raw_body.decode()):
        return JSONResponse({"error": "签名错误"}, status_code=400)

    body = await request.json()
    d = body.get("d")

    match body.get("op"):
        case 0:
            # print(body)
            content = d.get("content")
            if type(content) is not str:
                print("无效内容")
                return JSONResponse({"error": "无效内容"}), 400

            # print(f"收到消息：{content}")

            event_type = body["t"]
            author_id = d["author"]["id"]
            msg_id = d["id"]

            global last_msg_ids
            if msg_id in last_msg_ids:
                print("重复对话")
                return JSONResponse({"error": "重复对话"}), 400
            else:
                last_msg_ids.append(msg_id)

            global chats

            match event_type:
                case "GROUP_AT_MESSAGE_CREATE":
                    group_id = d["group_openid"]
                    if group_id not in chats:
                        chats[group_id] = ark.ArkResponseChat()

                    qqapi.group_reply(
                        group_id,
                        event_type,
                        msg_id,
                        chats[group_id].try_chat_with_cache(content, author_id),
                    )
                case "C2C_MESSAGE_CREATE":
                    if not chats.get(author_id):
                        chats[author_id] = ark.ArkResponseChat()

                    qqapi.users_dm_reply(
                        author_id,
                        event_type,
                        msg_id,
                        chats[author_id].try_chat_with_cache(content, author_id),
                    )
            return JSONResponse({}), 200
        case 13:
            outsign = qqapi.sign(d["event_ts"] + d["plain_token"])
            return JSONResponse(
                {"plain_token": d["plain_token"], "signature": outsign.hex()}
            ), 200


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
