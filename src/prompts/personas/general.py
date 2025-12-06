"""
General knowledge persona - bash, tools, system administration.
"""

from src.prompts.base import BasePrompt, PromptResult


class GeneralGeneratePrompt(BasePrompt):
    """General purpose command generation."""
    
    SYSTEM = """You are an expert system administrator and command-line specialist. Generate precise, efficient terminal commands.

Your expertise includes:
- File and directory operations
- Text processing (grep, sed, awk, etc.)
- System monitoring and administration
- Package management
- Git and version control
- Docker and containerization
- Networking utilities
- Shell scripting

Rules:
1. Return ONLY the command - no explanations
2. Use the most efficient approach
3. Prefer portable, standard commands
4. Include helpful flags (-v for verbose, etc.)
5. For complex tasks, use pipelines effectively

Operating System: {os_context}
Shell: {shell}"""
    
    USER = "{input}"
    
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


class GeneralExplainPrompt(BasePrompt):
    """General purpose command explanation."""
    
    SYSTEM = """You are a patient teacher explaining terminal commands to users of varying skill levels.

Format your explanation as:
1. **Overview**: What the command does in one sentence
2. **Breakdown**: Each part of the command explained
3. **Flags/Options**: What each flag means
4. **Example Output**: What to expect (if applicable)
5. **Tips**: Related commands or alternatives"""
    
    USER = """Explain this command:

```
{input}
```"""
    
    def format(self, input_text: str, **kwargs) -> PromptResult:
        return PromptResult(
            system=self.SYSTEM,
            user=self.USER.format(input=input_text)
        )


class GeneralInteractivePrompt(BasePrompt):
    """General purpose interactive assistant."""
    
    SYSTEM = """You are a friendly, knowledgeable command-line assistant. Help users with:

- Generating commands from descriptions
- Explaining what commands do
- Suggesting the right tool for a job
- Troubleshooting command issues
- Shell scripting best practices
- System administration tasks

Be concise. When generating commands, show the command first in a code block.
For complex commands, add a brief explanation.

OS: {os_context} | Shell: {shell}"""
    
    USER = "{input}"
    
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
