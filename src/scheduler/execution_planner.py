import uuid
from typing import List, Dict
from src.utils.logger import get_logger
from src.models.plan import ExecutionPlan
from src.models.scheduler import ExecutionNode, TaskGraph, ExecutionStrategy, ResourceLock, ResourceType

logger = get_logger("scheduler.execution_planner")

class ExecutionPlanner:
    """
    Applies deterministic rules to execution payloads to generate a TaskGraph.
    Assigns priorities, resource locks, and strict dependencies based on Tool names.
    """
    
    @staticmethod
    def build_graph(plans: List[ExecutionPlan], knowledge_requests: List[Dict[str, str]]) -> TaskGraph:
        """
        Builds the DAG from automation plans and knowledge requests.
        """
        graph = TaskGraph()
        
        # 1. Add Knowledge Requests (Always Parallel, High Priority, Background)
        for req in knowledge_requests:
            node_id = str(uuid.uuid4())
            node = ExecutionNode(
                id=node_id,
                handler_type="KnowledgeHandler",
                payload=req,
                execution_strategy=ExecutionStrategy.BACKGROUND,
                priority=2, # Medium priority
                dependencies=[],
                resource_requirements=[] # No locks needed
            )
            graph.add_node(node)
            
        # 2. Add Automation Plans
        for plan in plans:
            previous_node_id = None
            
            for item in plan.plan:
                node_id = str(uuid.uuid4())
                
                # Default rules
                priority = 1
                strategy = ExecutionStrategy.SEQUENTIAL
                resources = []
                dependencies = []
                
                # Rule Engine (Tool-specific analysis)
                tool = item.tool.lower()
                
                if tool in ("open_application", "focus_window", "wait_for_window"):
                    resources.append(ResourceLock(resource_type=ResourceType.APPLICATION, identifier="system_ui", exclusive=True))
                    strategy = ExecutionStrategy.EXCLUSIVE
                elif tool in ("type_text", "click_element", "read_text", "scroll_window", "wait_for_element"):
                    resources.append(ResourceLock(resource_type=ResourceType.APPLICATION, identifier="system_ui", exclusive=True))
                    strategy = ExecutionStrategy.EXCLUSIVE
                    # Strict sequential dependency within the same workflow
                    if previous_node_id:
                        dependencies.append(previous_node_id)
                        
                node = ExecutionNode(
                    id=node_id,
                    handler_type="AutomationHandler",
                    payload=item, # The PlanItem is passed directly to AutomationHandler
                    execution_strategy=strategy,
                    priority=priority,
                    dependencies=dependencies,
                    resource_requirements=resources
                )
                graph.add_node(node)
                previous_node_id = node_id
                
        logger.info(f"ExecutionPlanner built DAG with {len(graph.nodes)} nodes.")
        return graph
