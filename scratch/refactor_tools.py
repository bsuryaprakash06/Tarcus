import os
import re

TOOLS_DIR = r"C:\Users\Shane\Documents\Windows-Automation-1\Voice-Assistant\src\tools"

def refactor_tool_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip __init__, registry, base_tool
    if os.path.basename(filepath) in ["__init__.py", "registry.py", "base_tool.py", "__pycache__"]:
        return

    # 1. Add ErrorCode import if not present
    if "from src.models.error_codes import ErrorCode" not in content:
        content = re.sub(
            r"(from src\.models\.plan import ToolResult.*)",
            r"\1\nfrom src.models.error_codes import ErrorCode",
            content
        )

    # 2. Replace generic Exception catch with error_result
    # try: ... except Exception as e: return ToolResult(..., message=f"...", ...)
    content = re.sub(
        r"except Exception as e:\s+return ToolResult\(\s*tool_name=self\.name,\s*success=False,\s*message=[^,]+,\s*duration=0\.0\s*\)",
        r"except Exception as e:\n            return self.error_result(e)",
        content
    )

    # 3. Replace other ToolResult calls
    # We will just write a custom replacer for ToolResult(..., message=..., ...)
    def replacer(match):
        full_match = match.group(0)
        # Extract message content
        msg_match = re.search(r'message=(f?".*?"),\s*duration', full_match, flags=re.DOTALL)
        if not msg_match:
            return full_match
            
        msg = msg_match.group(1)
        
        # Decide if success=True or False
        is_success = "success=True" in full_match
        
        if is_success:
            user_msg = ""
            if "DRY RUN" in msg:
                user_msg = msg.replace("[DRY RUN] Would", "Simulating").replace("[DRY RUN]", "Simulating")
            else:
                user_msg = "Action completed successfully."
                # We can refine user_message manually later, for now give a generic success or derive it
                if "open" in msg.lower(): user_msg = f"Opened the requested item."
                elif "clos" in msg.lower(): user_msg = f"Closed the application."
                elif "creat" in msg.lower(): user_msg = f"Created successfully."
                elif "mov" in msg.lower(): user_msg = f"Moved successfully."
                elif "renam" in msg.lower(): user_msg = f"Renamed successfully."
                elif "delet" in msg.lower(): user_msg = f"Deleted successfully."
                elif "cop" in msg.lower(): user_msg = f"Copied to clipboard."
                elif "read" in msg.lower(): user_msg = f"Read clipboard."
            
            replacement = f'user_message="{user_msg}",\n                    developer_message={msg},\n                    duration'
        else:
            user_msg = "I couldn't complete that action."
            if "must be provided" in msg or "Missing" in msg:
                user_msg = "I'm missing some required information."
            
            replacement = f'user_message="{user_msg}",\n                    developer_message={msg},\n                    error_code=ErrorCode.VALIDATION_ERROR,\n                    duration'
            
        return full_match.replace(msg_match.group(0), replacement)

    content = re.sub(r'ToolResult\([\s\S]*?duration=0\.0\s*\)', replacer, content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

for root, _, files in os.walk(TOOLS_DIR):
    for file in files:
        if file.endswith(".py"):
            refactor_tool_file(os.path.join(root, file))

print("Refactoring complete.")
