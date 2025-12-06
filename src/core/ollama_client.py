"""
Ollama API client for Command Explainer.
Provides async interface to local Ollama instance.
"""

import asyncio
from typing import AsyncGenerator, Optional, List, Dict, Any

import httpx
from rich.console import Console

from src.config.settings import get_settings


console = Console()


class OllamaError(Exception):
    """Base exception for Ollama client errors."""
    pass


class OllamaConnectionError(OllamaError):
    """Raised when unable to connect to Ollama."""
    pass


class OllamaModelNotFoundError(OllamaError):
    """Raised when the specified model is not available."""
    pass


class OllamaClient:
    """
    Async client for Ollama API.
    
    Supports both streaming and non-streaming responses.
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        settings = get_settings()
        self.host = host or settings.ollama.host
        self.model = model or settings.get_model()
        self.timeout = timeout or settings.ollama.timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self) -> "OllamaClient":
        self._client = httpx.AsyncClient(
            base_url=self.host,
            timeout=httpx.Timeout(self.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure we have an active HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.host,
                timeout=httpx.Timeout(self.timeout)
            )
        return self._client
    
    async def check_health(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            client = await self._ensure_client()
            response = await client.get("/api/version")
            return response.status_code == 200
        except httpx.ConnectError:
            return False
        except Exception:
            return False
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List all available models in Ollama."""
        try:
            client = await self._ensure_client()
            response = await client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except httpx.ConnectError as e:
            raise OllamaConnectionError(
                f"Cannot connect to Ollama at {self.host}. Is it running?"
            ) from e
    
    async def model_exists(self, model_name: Optional[str] = None) -> bool:
        """Check if a specific model is available."""
        model = model_name or self.model
        try:
            models = await self.list_models()
            model_names = [m.get("name", "").split(":")[0] for m in models]
            # Also check full name with tag
            full_names = [m.get("name", "") for m in models]
            return model in model_names or model in full_names or model.split(":")[0] in model_names
        except OllamaError:
            return False
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        stream: bool = False
    ) -> str | AsyncGenerator[str, None]:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user prompt
            system: Optional system prompt
            model: Override the default model
            stream: If True, return an async generator for streaming
            
        Returns:
            Complete response string, or async generator if streaming
        """
        if stream:
            return self._generate_stream(prompt, system, model)
        return await self._generate_complete(prompt, system, model)
    
    async def _generate_complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None
    ) -> str:
        """Generate a complete (non-streaming) response."""
        client = await self._ensure_client()
        
        payload = {
            "model": model or self.model,
            "prompt": prompt,
            "stream": False
        }
        
        if system:
            payload["system"] = system
        
        try:
            response = await client.post("/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except httpx.ConnectError as e:
            raise OllamaConnectionError(
                f"Cannot connect to Ollama at {self.host}. Is it running?"
            ) from e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise OllamaModelNotFoundError(
                    f"Model '{model or self.model}' not found. Run: ollama pull {model or self.model}"
                ) from e
            raise OllamaError(f"Ollama API error: {e}") from e
    
    async def _generate_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response."""
        client = await self._ensure_client()
        
        payload = {
            "model": model or self.model,
            "prompt": prompt,
            "stream": True
        }
        
        if system:
            payload["system"] = system
        
        try:
            async with client.stream("POST", "/api/generate", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
        except httpx.ConnectError as e:
            raise OllamaConnectionError(
                f"Cannot connect to Ollama at {self.host}. Is it running?"
            ) from e
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
