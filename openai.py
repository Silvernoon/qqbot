import requests


def chat_with_model(token, content: str):
    url = "http://localhost:8070/api/chat/completions"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "model": "deepseek-v3-1-terminus",
        "messages": [{"role": "user", "content": content}],
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()
