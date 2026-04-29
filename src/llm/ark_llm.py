from typing import Optional
from .openai_llm import OpenAIClient
import os
import warnings
import time


class ArkClient(OpenAIClient):
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_key_env_var: str = "ARK_API_KEY",
        model: str = "deepseek-v3-2-251201",
    ) -> None:
        try:
            import volcenginesdkarkruntime as Ark
        except ImportError:
            raise ValueError(
                'The volcenginesdkarkruntime python package is not installed. Please install it with `pip install "volcengine-python-sdk[ark]"`'
            )

        if api_key is not None:
            warnings.warn(
                "Direct api_key configuration will not be persisted. "
                "Please use environment variables via api_key_env_var for persistent storage.",
                DeprecationWarning,
            )

        self.api_key_env_var = api_key_env_var
        self.api_key = api_key or os.getenv(api_key_env_var)
        if not self.api_key:
            raise ValueError(f"The {api_key_env_var} environment variable is not set.")

        self.client = Ark.Ark(api_key=api_key)
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3"

        # default model
        self.model = model


class ArkResponseChat(ArkClient):
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_key_env_var: str = "ARK_API_KEY",
        model: str = "deepseek-v3-2-251201",
    ) -> None:
        super().__init__(api_key, api_key_env_var, model)

        self.previous_response_id: str | None
        self.last_timestamp: int | None

    def try_chat_with_cache(self, content):
        if (
            self.previous_response_id
            and self.last_timestamp
            and self.last_timestamp > time.time()
        ):
            return self.chat_with_cache(content)

        return self.chat_with_cache(
            [
                {
                    "role": "system",
                    "content": self.system_prompt,
                },
                {
                    "role": "user",
                    "content": content,
                },
            ]
        )

    def chat_with_cache(self, input, ttl: int = 3600):
        from volcenginesdkarkruntime.types.responses.response import Response
        from volcenginesdkarkruntime.types.responses import ResponseOutputMessage

        rep = self.client.responses.create(
            model=self.model,
            caching={"type": "enabled"},
            input=input,
            thinking={"type": "disabled"},
            expire_at=int(time.time()) + ttl,
        )

        # debug
        # print(rep)

        if isinstance(rep, Response):
            self.previous_response_id = rep.previous_response_id
            self.last_timestamp = rep.expire_at

            message = rep.output[0]

            if isinstance(message, ResponseOutputMessage):
                message.content[0].text

    def delete_cache(self, response_id: str = ""):
        if not response_id and self.previous_response_id:
            response_id = self.previous_response_id

        return self.client.responses.delete(response_id)
