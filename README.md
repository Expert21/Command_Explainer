# Command Explainer (cmdex)

A terminal command generator and explainer powered by local LLM via Ollama. Generate commands from natural language, or get clear explanations of complex terminal commands.

## Features

- **Generate Commands**: Describe what you want in plain English, get the terminal command
- **Explain Commands**: Paste a complex command, get a clear breakdown
- **Interactive Mode**: REPL-style interface for continuous assistance
- **Persona System**: Switch between general and security-focused modes
- **Future-Ready**: Architecture supports LoRA fine-tuning for specialized domains

## Requirements

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally
- Recommended model: `dolphin-mistral:7b` (best accuracy)
- Low-RAM alternative: `qwen2.5:3b` (~2.3GB RAM, reduced accuracy)

## Installation

```bash
# Clone/Download the project
cd Command_Explainer

# Install dependencies
pip install -e .

# Pull the recommended model
ollama pull dolphin-mistral:7b

# OR for systems with limited RAM (8GB or less)
ollama pull qwen2.5:3b
```

## Usage

### Interactive Mode (Default)

Simply run `cmdex` without arguments:

```bash
cmdex
```

This opens an interactive session where you can:
- Ask questions naturally
- Use `/generate <description>` to create commands
- Use `/explain <command>` to understand commands
- Use `/persona security` to switch to security mode

### Generate a Command

```bash
cmdex generate "find all python files modified in the last week"
# Output: find . -name "*.py" -mtime -7
```

### Explain a Command

```bash
cmdex explain "curl -X POST -H 'Content-Type: application/json' -d '{\"key\":\"value\"}' https://api.example.com"
```

### Use Security Persona

```bash
cmdex --persona security
# or
cmdex generate -p security "scan for open ports on target"
```

### List Available Models

```bash
cmdex models list
```

## Configuration

Edit `config.yaml` to customize:

```yaml
ollama:
  host: "http://localhost:11434"
  model: "dolphin-mistral:7b"  # or qwen2.5:3b for low-RAM systems
  timeout: 120

personas:
  default: "general"
  available:
    - general
    - security
```

## Personas

### General
Default persona for everyday terminal tasks:
- File operations
- System administration
- Git and version control
- Package management
- Shell scripting

### Security
Comprehensive cybersecurity assistant covering:
- Penetration testing
- Network security
- Digital forensics
- Malware analysis
- Incident response

## Future Development

- LoRA fine-tuning for domain-specific models
- Plugin system for tool-specific integrations
- Command history and favorites
- Shell integration for direct execution

## License

MIT
