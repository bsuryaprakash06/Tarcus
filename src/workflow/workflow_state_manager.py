import os
import json
from typing import Optional
from src.models.workflow import Workflow
from src.utils.logger import get_logger

logger = get_logger("workflow.state_manager")

class WorkflowStateManager:
    """Handles serialization and recovery of workflows to survive crashes and pauses."""
    
    def __init__(self, data_dir: str = "data/workflows"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
    def _get_file_path(self, workflow_id: str) -> str:
        return os.path.join(self.data_dir, f"{workflow_id}.json")
        
    def save(self, workflow: Workflow) -> None:
        """Serializes the workflow state to disk."""
        try:
            path = self._get_file_path(workflow.workflow_id)
            with open(path, "w", encoding="utf-8") as f:
                f.write(workflow.model_dump_json(indent=2))
            logger.debug(f"Saved workflow state: {workflow.workflow_id}")
        except Exception as e:
            logger.error(f"Failed to serialize workflow {workflow.workflow_id}: {e}")
            
    def load(self, workflow_id: str) -> Optional[Workflow]:
        """Loads a workflow state from disk."""
        path = self._get_file_path(workflow_id)
        if not os.path.exists(path):
            return None
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Workflow(**data)
        except Exception as e:
            logger.error(f"Failed to deserialize workflow {workflow_id}: {e}")
            return None
            
    def delete(self, workflow_id: str) -> None:
        """Cleans up the workflow state file after successful completion."""
        path = self._get_file_path(workflow_id)
        if os.path.exists(path):
            try:
                os.remove(path)
                logger.debug(f"Deleted workflow state: {workflow_id}")
            except Exception as e:
                logger.error(f"Failed to delete workflow state {workflow_id}: {e}")
