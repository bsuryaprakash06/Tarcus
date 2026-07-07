import uuid
from typing import Dict, Any
from src.events.pipeline_events import PipelineEventBus, PipelineEventType
from src.models.context_scope import AutomationEntity
from src.utils.logger import get_logger

logger = get_logger("context.tracker")

class EntityTracker:
    """Event-driven entity extractor that populates strongly typed memory buckets."""
    
    def __init__(self, context_service):
        self.context_service = context_service
        self.event_bus = PipelineEventBus()
        self._subscribe_events()
        
    def _subscribe_events(self):
        self.event_bus.subscribe(PipelineEventType.STEP_COMPLETED, self._on_step_completed)
        self.event_bus.subscribe(PipelineEventType.KNOWLEDGE_GENERATED, self._on_knowledge_generated)
        self.event_bus.subscribe(PipelineEventType.WORKFLOW_STARTED, self._on_workflow_started)
        self.event_bus.subscribe(PipelineEventType.WORKFLOW_COMPLETED, self._on_workflow_completed)

    def _on_step_completed(self, payload: Dict[str, Any]):
        """Extract automation entities purely from the validated execution ToolResult."""
        result_dict = payload.get("result", {})
        if not isinstance(result_dict, dict):
            return
            
        entities = result_dict.get("entities", [])
        tool_name = result_dict.get("tool_name", "")
        data = result_dict.get("data", {})
        
        if tool_name == "open_application":
            app_name = data.get("application", "")
            if app_name:
                entity = AutomationEntity(
                    id=str(uuid.uuid4()),
                    type="Application",
                    name=app_name,
                    tool=tool_name,
                    metadata={"pid": data.get("pid")}
                )
                self.context_service.automation_context.add_entity(entity, "applications")
                logger.debug(f"Tracked application: {app_name}")
                
        elif tool_name in ("create_folder", "open_folder", "rename_folder"):
            folder_name = data.get("folder_name", "") or data.get("path", "")
            if folder_name:
                entity = AutomationEntity(
                    id=str(uuid.uuid4()),
                    type="Folder",
                    name=folder_name,
                    tool=tool_name
                )
                self.context_service.automation_context.add_entity(entity, "folders")
                
        elif tool_name in ("create_file", "write_file", "read_file"):
            file_name = data.get("file_name", "") or data.get("path", "")
            if file_name:
                entity = AutomationEntity(
                    id=str(uuid.uuid4()),
                    type="File",
                    name=file_name,
                    tool=tool_name
                )
                self.context_service.automation_context.add_entity(entity, "files")

    def _on_knowledge_generated(self, payload: Dict[str, Any]):
        topic = payload.get("primary_topic")
        if topic:
            kc = self.context_service.knowledge_context
            if kc.current_topic and kc.current_topic != topic:
                kc.previous_topic = kc.current_topic
            kc.current_topic = topic
            logger.debug(f"Tracked knowledge topic: {topic}")

    def _on_workflow_started(self, payload: Dict[str, Any]):
        wf_id = payload.get("workflow_id")
        self.context_service.workflow_context.active_workflow = wf_id

    def _on_workflow_completed(self, payload: Dict[str, Any]):
        self.context_service.workflow_context.active_workflow = None
