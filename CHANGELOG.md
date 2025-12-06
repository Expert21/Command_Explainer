# Changelog

All notable changes to Command Explainer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-05

### Added
- **Interactive Mode**: REPL-style interface with streaming responses
- **Command Generation**: Natural language to terminal command conversion
- **Command Explanation**: Detailed breakdowns of complex commands
- **Persona System**: Switch between `general` and `security` modes
- **OS/Shell Detection**: Context-aware responses for Linux/macOS/Windows
- **Model Configuration**: Configurable Ollama model via `config.yaml`

### Tested Models
- `qwen2.5:1.5b` - **Recommended** (best speed/accuracy for 8GB RAM systems)
- `dolphin-phi:2.7b` - Good accuracy, slower
- `tinyllama:1.1b` - Fast but occasional hallucinations
- `qwen2.5:0.5b` - Too many errors
- `smollm:135m` - Not recommended (unusable quality)

### Notes
- v1.0 will include fine-tuned system prompts
- LoRA adapters planned for enhanced security persona
