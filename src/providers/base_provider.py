from abc import ABC, abstractmethod
from pydantic import BaseModel, Field

class ProviderResponse(BaseModel):
    """Data model representing a structured response from any LLM provider."""
    text: str = Field(description="The raw string content returned by the model.")
    model_name: str = Field(description="The specific model ID that generated the response.")
    provider_name: str = Field(description="The provider name (e.g. 'ollama', 'openai', 'groq').")
    latency: float = Field(description="The latency of the API call in seconds.")
    usage: dict = Field(default_factory=dict, description="Metadata containing token usage (e.g., input, output, total).")

class BaseProvider(ABC):
    """Abstract base class representing an LLM backend provider."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """The identifier name of the provider."""
        pass

    @property
    @abstractmethod
    def supports_json_mode(self) -> bool:
        """Whether the provider/model natively supports JSON response formatting."""
        pass

    @property
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Whether the provider supports stream generation responses."""
        pass

    @property
    @abstractmethod
    def supports_vision(self) -> bool:
        """Whether the provider supports multimodal vision capabilities."""
        pass

    @property
    @abstractmethod
    def supports_tool_calling(self) -> bool:
        """Whether the provider natively supports function/tool calling schemas."""
        pass

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, require_json: bool = False) -> ProviderResponse:
        """
        Communicates with the LLM backend to generate a response.

        Args:
            system_prompt: System-level instruction context.
            user_prompt: User command input text.

        Returns:
            ProviderResponse: Structured details of the LLM response.
        """
        pass
