from src.tools.registry import ToolRegistry
from src.brain.prompts import SYSTEM_PROMPT_TEMPLATE

class PromptBuilder:
    """Builder class responsible for dynamically generating system prompts from tool registry metadata."""
    
    def __init__(self, tool_registry: ToolRegistry):
        self.registry = tool_registry

    def build_prompt(self) -> str:
        """
        Dynamically constructs the system prompt containing descriptions, arguments schema,
        examples, safety levels, and categories for all registered tools.
        """
        descriptions = []
        for tool in self.registry.list_tools():
            desc = f"- Tool: {tool.name} (v{tool.version})\n"
            desc += f"  Category: {tool.category}\n"
            desc += f"  Description: {tool.description}\n"
            desc += f"  Safety Level: {tool.safety_level.name}\n"
            desc += "  Arguments:\n"
            for arg_name, arg_info in tool.arguments_schema.items():
                desc += f"    - {arg_name} ({arg_info.get('type')}): {arg_info.get('description')}\n"
            desc += "  Examples:\n"
            for example in tool.examples:
                desc += f"    - \"{example}\"\n"
            descriptions.append(desc)
            
        tools_description = "\n".join(descriptions)
        return SYSTEM_PROMPT_TEMPLATE.format(tools_description=tools_description)
