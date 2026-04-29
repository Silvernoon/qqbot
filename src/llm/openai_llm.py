from .llm import LLMHander
import requests
from typing import Optional
import warnings
import os


class OpenAIClient(LLMHander):
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_key_env_var: str = "ARK_API_KEY",
    ) -> None:
        try:
            import openai
        except ImportError:
            raise ValueError(
                "The openai python package is not installed. Please install it with `pip install openai`"
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

        self.client = openai.Client(api_key=api_key)
        # TODO: compelete
        self.base_url = ""

    def get_models_list(self):
        return requests.get(
            self.base_url + "/models",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        ).json()
