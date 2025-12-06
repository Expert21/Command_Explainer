"""
Configuration settings management for Command Explainer.
Loads settings from config.yaml and environment variables.
"""

import os
from pathlib import Path
from typing import Optional, List

import yaml
from pydantic import BaseModel, Field


class OllamaSettings(BaseModel):
    """Ollama API configuration."""
    host: str = "http://localhost:11434"
    model: str = "dolphin-phi:2.7b"
    timeout: int = 120


class PersonaSettings(BaseModel):
    """Persona configuration."""
    default: str = "general"
    available: List[str] = Field(default_factory=lambda: ["general", "security"])


class Settings(BaseModel):
    """Application settings."""
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    personas: PersonaSettings = Field(default_factory=PersonaSettings)
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Settings":
        """
        Load settings from config file.
        
        Searches for config.yaml in:
        1. Provided path
        2. Current directory
        3. User's home directory (~/.cmdex/config.yaml)
        """
        search_paths = []
        
        if config_path:
            search_paths.append(Path(config_path))
        
        search_paths.extend([
            Path.cwd() / "config.yaml",
            Path.home() / ".cmdex" / "config.yaml",
        ])
        
        for path in search_paths:
            if path.exists():
                with open(path, "r") as f:
                    data = yaml.safe_load(f)
                    return cls.model_validate(data) if data else cls()
        
        # Return defaults if no config found
        return cls()
    
    def get_model(self) -> str:
        """Get the configured Ollama model, with env override support."""
        return os.environ.get("CMDEX_MODEL", self.ollama.model)
    
    def get_persona(self) -> str:
        """Get the default persona, with env override support."""
        return os.environ.get("CMDEX_PERSONA", self.personas.default)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings.load()
    return _settings


def reload_settings(config_path: Optional[Path] = None) -> Settings:
    """Reload settings from config file."""
    global _settings
    _settings = Settings.load(config_path)
    return _settings
