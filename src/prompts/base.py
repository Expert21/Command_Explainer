"""
Base prompt templates for command generation and explanation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class PromptResult:
    """Result from prompt formatting."""
    system: str
    user: str


class BasePrompt(ABC):
    """Base class for all prompt templates."""
    
    @abstractmethod
    def format(self, input_text: str, **kwargs) -> PromptResult:
        """Format the prompt with the given input."""
        pass


class GeneratePrompt(BasePrompt):
    """Prompt template for generating terminal commands from natural language."""
    
    SYSTEM = """You are a terminal command expert. Your task is to convert natural language descriptions into precise terminal commands.

Rules:
1. Return ONLY the command(s) needed - no explanations unless asked
2. If multiple commands are needed, separate them with && or use a script format
3. Prefer common, portable commands when possible
4. Include necessary flags and options
5. If the request is ambiguous, provide the most likely intended command
6. For dangerous operations (rm -rf, etc.), include appropriate safety measures

Operating System Context: {os_context}
Shell: {shell}"""
    
    USER = """Convert this to a terminal command:

{input}

Respond with ONLY the command, nothing else."""
    
    def format(
        self,
        input_text: str,
        os_context: str = "Linux/Unix",
        shell: str = "bash"
    ) -> PromptResult:
        return PromptResult(
            system=self.SYSTEM.format(os_context=os_context, shell=shell),
            user=self.USER.format(input=input_text)
        )


class ExplainPrompt(BasePrompt):
    """Prompt template for explaining terminal commands."""
    
    SYSTEM = """You are a terminal command educator. Your task is to explain commands in clear, understandable language.

Rules:
1. Break down the command into its components
2. Explain each flag and option
3. Describe what the command does overall
4. Mention any potential risks or side effects
5. Suggest safer alternatives if the command is dangerous
6. Use simple language - avoid jargon unless necessary"""
    
    USER = """Explain this terminal command in clear language:

```
{input}
```

Break it down step by step."""
    
    def format(self, input_text: str, **kwargs) -> PromptResult:
        return PromptResult(
            system=self.SYSTEM,
            user=self.USER.format(input=input_text)
        )


class InteractivePrompt(BasePrompt):
    """Prompt for interactive/conversational mode."""
    
    SYSTEM = """You are a helpful terminal and command-line assistant. You can:
1. Generate commands from natural language descriptions
2. Explain what commands do
3. Suggest tools for specific tasks
4. Help debug command issues
5. Provide best practices for shell scripting

Be concise but thorough. When generating commands, show the command first, then optionally explain if it's complex.

Operating System: {os_context}
Shell: {shell}

Current persona: {persona}"""
    
    USER = "{input}"
    
    def format(
        self,
        input_text: str,
        os_context: str = "Linux/Unix",
        shell: str = "bash",
        persona: str = "general"
    ) -> PromptResult:
        return PromptResult(
            system=self.SYSTEM.format(
                os_context=os_context,
                shell=shell,
                persona=persona
            ),
            user=self.USER.format(input=input_text)
        )
