"""
Core engine orchestrating command generation and explanation.
"""

import platform
import os
from typing import Optional, AsyncGenerator
from enum import Enum

from src.core.ollama_client import OllamaClient
from src.prompts.base import GeneratePrompt, ExplainPrompt, InteractivePrompt
from src.prompts.personas.general import (
    GeneralGeneratePrompt,
    GeneralExplainPrompt, 
    GeneralInteractivePrompt
)
from src.prompts.personas.security import (
    SecurityGeneratePrompt,
    SecurityExplainPrompt,
    SecurityInteractivePrompt
)
from src.config.settings import get_settings


class Persona(str, Enum):
    """Available personas for command generation/explanation."""
    GENERAL = "general"
    SECURITY = "security"


class CommandEngine:
    """
    Core engine for command generation and explanation.
    
    Orchestrates between Ollama client and prompt templates,
    handling persona switching and context detection.
    """
    
    def __init__(
        self,
        client: Optional[OllamaClient] = None,
        persona: Optional[Persona] = None
    ):
        self.client = client or OllamaClient()
        settings = get_settings()
        self.persona = persona or Persona(settings.get_persona())
        
        # Detect OS context
        self.os_context = self._detect_os()
        self.shell = self._detect_shell()
    
    def _detect_os(self) -> str:
        """Detect the current operating system."""
        system = platform.system()
        if system == "Windows":
            return "Windows"
        elif system == "Darwin":
            return "macOS"
        else:
            return "Linux/Unix"
    
    def _detect_shell(self) -> str:
        """Detect the current shell."""
        shell = os.environ.get("SHELL", "")
        if "zsh" in shell:
            return "zsh"
        elif "fish" in shell:
            return "fish"
        elif "powershell" in shell.lower() or platform.system() == "Windows":
            return "PowerShell"
        return "bash"
    
    def _get_prompts(self):
        """Get the appropriate prompts for the current persona."""
        if self.persona == Persona.SECURITY:
            return (
                SecurityGeneratePrompt(),
                SecurityExplainPrompt(),
                SecurityInteractivePrompt()
            )
        else:
            return (
                GeneralGeneratePrompt(),
                GeneralExplainPrompt(),
                GeneralInteractivePrompt()
            )
    
    def set_persona(self, persona: Persona):
        """Switch to a different persona."""
        self.persona = persona
    
    async def generate(
        self,
        description: str,
        stream: bool = False
    ) -> str | AsyncGenerator[str, None]:
        """
        Generate a terminal command from natural language.
        
        Args:
            description: Natural language description of what the command should do
            stream: If True, return an async generator for streaming output
            
        Returns:
            The generated command string, or async generator if streaming
        """
        generate_prompt, _, _ = self._get_prompts()
        
        prompt_result = generate_prompt.format(
            description,
            os_context=self.os_context,
            shell=self.shell
        )
        
        return await self.client.generate(
            prompt=prompt_result.user,
            system=prompt_result.system,
            stream=stream
        )
    
    async def explain(
        self,
        command: str,
        stream: bool = False
    ) -> str | AsyncGenerator[str, None]:
        """
        Explain what a terminal command does.
        
        Args:
            command: The command to explain
            stream: If True, return an async generator for streaming output
            
        Returns:
            The explanation string, or async generator if streaming
        """
        _, explain_prompt, _ = self._get_prompts()
        
        prompt_result = explain_prompt.format(command)
        
        return await self.client.generate(
            prompt=prompt_result.user,
            system=prompt_result.system,
            stream=stream
        )
    
    async def chat(
        self,
        message: str,
        stream: bool = True
    ) -> str | AsyncGenerator[str, None]:
        """
        Interactive chat mode for general assistance.
        
        Args:
            message: User's message/question
            stream: If True, return an async generator for streaming output
            
        Returns:
            The response string, or async generator if streaming
        """
        _, _, interactive_prompt = self._get_prompts()
        
        prompt_result = interactive_prompt.format(
            message,
            os_context=self.os_context,
            shell=self.shell
        )
        
        return await self.client.generate(
            prompt=prompt_result.user,
            system=prompt_result.system,
            stream=stream
        )
    
    async def check_connection(self) -> bool:
        """Check if Ollama is accessible."""
        return await self.client.check_health()
    
    async def list_models(self):
        """List available Ollama models."""
        return await self.client.list_models()
    
    async def close(self):
        """Clean up resources."""
        await self.client.close()
