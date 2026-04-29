from chromadb.api.types import Embeddings, Embeddable, EmbeddingFunction, Space
from typing import List, Dict, Any, Optional
import os
import numpy as np
from chromadb.utils.embedding_functions.schemas import validate_config_schema
import warnings
from chromadb.utils.embedding_functions import register_embedding_function


@register_embedding_function
class ArkEmbeddingFunction(EmbeddingFunction[Embeddable]):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-ada-002",
        organization_id: Optional[str] = None,
        api_base: Optional[str] = None,
        default_headers: Optional[Dict[str, str]] = None,
        api_key_env_var: str = "API_KEY",
    ):
        """
        Initialize the OpenAIEmbeddingFunction.
        Args:
            api_key_env_var (str, optional): Environment variable name that contains your API key for the OpenAI API.
                Defaults to "CHROMA_OPENAI_API_KEY".
            model_name (str, optional): The name of the model to use for text
                embeddings. Defaults to "text-embedding-ada-002".
            organization_id(str, optional): The OpenAI organization ID if applicable
            api_base (str, optional): The base path for the API. If not provided,
                it will use the base path for the OpenAI API. This can be used to
                point to a different deployment, such as an Azure deployment.
            default_headers (Dict[str, str], optional): A mapping of default headers to be sent with each API request.
        """
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

        self.model = model
        self.organization_id = organization_id
        self.api_base = api_base
        self.default_headers = default_headers

        # Initialize the OpenAI client
        client_params: Dict[str, Any] = {"api_key": self.api_key}

        if self.organization_id is not None:
            client_params["organization"] = self.organization_id
        if self.api_base is not None:
            client_params["base_url"] = self.api_base
        if self.default_headers is not None:
            client_params["default_headers"] = self.default_headers

        self.client = Ark.Ark(api_key=self.api_key)

    def __call__(self, input: Embeddable) -> Embeddings:
        """
        Generate embeddings for the given documents or images.

        Args:
            input: Documents or images to generate embeddings for.

        Returns:
            Embeddings for the documents or images.
        """
        # Handle batching
        if not input:
            return []

        # Prepare embedding parameters
        embeddings = {}
        for item in input:
            # TODO: devide image_url and text
            embeddings = {"type": "text", "text": item}

        embedding_params: Dict[str, Any] = {
            "model": self.model,
            "input": [embeddings],
        }

        # Get embeddings
        response = self.client.multimodal_embeddings.create(**embedding_params)

        print(response.data.embedding)

        # Extract embeddings from response
        return [np.array(response.data.embedding, dtype=np.float32)]

    @staticmethod
    def name() -> str:
        return "openai"

    def default_space(self) -> Space:
        # OpenAI embeddings work best with cosine similarity
        return "cosine"

    def supported_spaces(self) -> List[Space]:
        return ["cosine", "l2", "ip"]

    @staticmethod
    def build_from_config(config: Dict[str, Any]) -> EmbeddingFunction[Embeddable]:
        # Extract parameters from config
        api_key_env_var = config.get("api_key_env_var")
        model = config.get("model")
        organization_id = config.get("organization_id")
        api_base = config.get("api_base")
        default_headers = config.get("default_headers")

        if api_key_env_var is None or model is None:
            assert False, "This code should not be reached"

        # Create and return the embedding function
        return ArkEmbeddingFunction(
            api_key_env_var=api_key_env_var,
            model=model,
            organization_id=organization_id,
            api_base=api_base,
            default_headers=default_headers,
        )

    def get_config(self) -> Dict[str, Any]:
        return {
            "api_key_env_var": self.api_key_env_var,
            "modele": self.model,
            "organization_id": self.organization_id,
            "api_base": self.api_base,
            "default_headers": self.default_headers,
        }

    def validate_config_update(
        self, old_config: Dict[str, Any], new_config: Dict[str, Any]
    ) -> None:
        if "model_name" in new_config:
            raise ValueError(
                "The model name cannot be changed after the embedding function has been initialized."
            )

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> None:
        """
        Validate the configuration using the JSON schema.

        Args:
            config: Configuration to validate

        Raises:
            ValidationError: If the configuration does not match the schema
        """
        validate_config_schema(config, "openai")
