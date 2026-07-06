import json
import uuid
from typing import List
from src.utils.logger import get_logger
from src.providers import get_provider_from_settings
from src.models.task_query import AtomicTask, DependencyType

logger = get_logger("task.decomposer")

class TaskDecomposer:
    def __init__(self):
        self.provider = get_provider_from_settings()
        
    def decompose(self, text: str) -> List[AtomicTask]:
        """Splits a single complex sentence into an ordered list of atomic tasks using the LLM."""
        
        system_prompt = (
            "You are a Task Decomposer. Break the following user request into a JSON array of independent, atomic tasks.\n"
            "Rules:\n"
            "1. Split compound sentences (e.g., 'Open notepad and type hello' -> 'Open notepad', 'Type hello').\n"
            "2. Preserve logical execution order.\n"
            "3. Make implicit references explicit (e.g., 'Save it' -> 'Save the file').\n"
            "4. Return ONLY valid JSON in this exact format: [{\"text\": \"...\", \"order\": 1}]"
        )
        
        try:
            # We use the underlying provider to avoid the Planner's specific Validation schemas
            response = self.provider.generate(system_prompt, f"User Request: {text}", require_json=True)
            raw_response = response.text
            
            # Clean markdown if present
            raw_response = raw_response.strip()
            if raw_response.startswith("```json"):
                raw_response = raw_response[7:]
            if raw_response.startswith("```"):
                raw_response = raw_response[3:]
            if raw_response.endswith("```"):
                raw_response = raw_response[:-3]
                
            parsed = json.loads(raw_response.strip())
            
            if isinstance(parsed, dict):
                if "tasks" in parsed:
                    parsed = parsed["tasks"]
                else:
                    for val in parsed.values():
                        if isinstance(val, list):
                            parsed = val
                            break
                    else:
                        raise ValueError("Could not find a list of tasks in the JSON response")
            
            tasks = []
            for item in parsed:
                tasks.append(
                    AtomicTask(
                        id=str(uuid.uuid4()),
                        text=item["text"],
                        order=item["order"]
                    )
                )
            
            if not tasks:
                raise ValueError("LLM returned empty task list")
                
            # Ensure sorting
            tasks.sort(key=lambda x: x.order)
            return tasks
            
        except Exception as e:
            logger.warning(f"Decomposition failed, falling back to single task: {e}")
            return [AtomicTask(id=str(uuid.uuid4()), text=text, order=1)]
