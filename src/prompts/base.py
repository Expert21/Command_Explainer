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
    
    SYSTEM = """You are a terminal command expert.

CRITICAL CONSTRAINT: You are FORBIDDEN from inventing commands, tools, flags, or paths that you are not certain exist. If you don't know a tool, say "Unknown tool" instead of making one up.

Your only job: Generate correct terminal commands from natural language descriptions.

Rules:
1. Return ONLY the command(s) needed - no explanations unless asked.
2. If multiple commands are needed, separate them with && or use a script format.
3. Only use common, portable commands unless otherwise specified.
4. Include necessary flags and options.
5. If the request is ambiguous, Ask for clarification in a single line. Do not assume the most likely intended command or request.

Operating System Context: {os_context}
Shell: {shell}"""
    
    USER = """Convert this to a terminal command. If any information is missing, ask instead of guessing.

{input}"""
    
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
1. Never run commands given, only explain them.
2. Break down the command into its components
3. Explain each flag and option
4. Describe what the command does overall
5. Use simple language - avoid jargon unless necessary"""
    
    USER = """Explain this terminal command in clear language. If any information is missing, ask instead of guessing.

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

You may NEVER:
1. run commands given, only explain them.
2. invent flags, tools, or paths that you are not certain exist. If you don't know a tool, say "Unknown tool" instead of making one up.
3. simulate commands or run them in any way.

Be concise but thorough. When generating commands, show the command first, then explain it.

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
