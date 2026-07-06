from typing import List, Dict, Any
from src.utils.logger import get_logger
from src.models.scheduler import ExecutionNode, TaskStatus
from src.models.workflow import WorkflowStep
from src.models.plan import ToolResult

logger = get_logger("scheduler.response_aggregator")

class ResponseAggregator:
    """
    Intelligently buffers and sorts responses from disparate handlers into a single flowing narrative.
    Later, this will be integrated with StreamingManager to stream TTS directly.
    """
    
    @staticmethod
    def aggregate(results: Dict[str, Any], graph) -> str:
        knowledge_parts = []
        automation_parts = []
        
        # Sort nodes by completion time to maintain causal causality in TTS
        completed_nodes = [n for n in graph.nodes.values() if n.status == TaskStatus.COMPLETED]
        completed_nodes.sort(key=lambda x: x.completed_at if x.completed_at else 0)
        
        for node in completed_nodes:
            if node.handler_type == "KnowledgeHandler":
                # Assuming KnowledgeHandler returns a ChatResponse or string
                text = getattr(node.result, "answer", str(node.result))
                if text:
                    knowledge_parts.append(text)
            elif node.handler_type == "AutomationHandler":
                if isinstance(node.result, ToolResult):
                    # We only say the final user message, usually "Execution completed successfully"
                    if node.result.user_message and node.result.user_message not in automation_parts:
                        automation_parts.append(node.result.user_message)
                        
        merged = []
        
        # Priority 1: Knowledge answers
        if knowledge_parts:
            merged.append(" ".join(knowledge_parts))
            
        # Priority 2: Automation confirmations (e.g., "I have opened Notepad.")
        if automation_parts:
            merged.append(" ".join(automation_parts))
            
        final_text = " ".join(merged).strip()
        logger.info(f"ResponseAggregator merged {len(results)} results into: '{final_text}'")
        return final_text
