import threading
import time
from src.services.session_manager import SessionManager
from src.models.input import InputSource, InputRequest
from src.events.pipeline_events import PipelineEventBus, PipelineEventType
from src.utils.logger import get_logger

# Legacy / Backend Services
from src.services.voice_service import VoiceService
from src.services.normalization_service import NormalizationService
from src.services.dialogue_manager import DialogueManager
from src.services.intent_router_service import IntentRouterService
from src.services.llm_service import LLMService
from src.services.workflow_service import WorkflowService
from src.services.response_formatter_service import ResponseFormatterService
from src.services.tts_service import TTSService
from src.services.llm_chat_service import LLMChatService
from src.services.conversation_service import ConversationService
from src.services.fallback_service import FallbackService
from src.safety.validator import SafetyValidator
from src.models.request_context import RequestContext
from src.models.response import ResponseProfile, ResponseMode
from src.utils.settings import DEFAULT_RESPONSE_STYLE

# New Scheduler Services
from src.task_decomposer.decomposer import TaskDecomposer
from src.execution.workflow_builder import WorkflowBuilder
from src.execution.execution_planner import ExecutionPlanner
from src.scheduler.scheduler import Scheduler
from src.scheduler.response_aggregator import ResponseAggregator
from src.models.scheduler import TaskGraph, ExecutionNode
from src.scheduler.response_aggregator import ResponseAggregator

logger = get_logger("pipeline.worker")

class PipelineWorker(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.session_manager = SessionManager()
        self.event_bus = PipelineEventBus()
        self._stop_event = threading.Event()
        
        self.voice_service = VoiceService()
        self.normalization_service = NormalizationService()
        self.dialogue_manager = DialogueManager()
        
        self.task_decomposer = TaskDecomposer()
        self.workflow_builder = WorkflowBuilder()
        self.execution_planner = ExecutionPlanner()
        self.scheduler_engine = Scheduler()
        self.response_aggregator = ResponseAggregator()
        
        self.router_service = IntentRouterService()
        self.llm_service = LLMService()
        self.workflow_service = WorkflowService()
        self.response_formatter = ResponseFormatterService()
        self.tts_service = TTSService()
        self.chat_service = LLMChatService()
        self.conversation_service = ConversationService()
        self.fallback_service = FallbackService()
        self.safety_validator = SafetyValidator()

    def stop(self):
        self._stop_event.set()

    def run(self):
        logger.info("Pipeline Worker Thread started.")
        while not self._stop_event.is_set():
            request = self.session_manager.dequeue()
            if not request:
                time.sleep(0.1)
                continue
                
            self.event_bus.publish(PipelineEventType.INPUT_RECEIVED, {"request_id": request.request_id, "text": request.text, "source": request.source.value})
            
            try:
                self._process_request(request)
            except Exception as e:
                logger.error(f"Pipeline crashed for request {request.request_id}: {e}")
                self.event_bus.publish(PipelineEventType.ERROR, {"error": str(e)})
                
            self.session_manager.complete_request()
            self.event_bus.publish(PipelineEventType.COMPLETED, {"request_id": request.request_id})

    def _process_request(self, request: InputRequest):
        context = RequestContext()
        text = request.text
        
        if request.source == InputSource.VOICE:
            result = self.voice_service.listen(context=context)
            text = result.text
            self.event_bus.publish(PipelineEventType.SPEECH_FINISHED, {"text": text})
            if not text.strip():
                self._respond("I didn't hear anything.", ResponseMode.ERROR)
                return

        if text.lower() in ("start over", "clear context", "forget this conversation", "reset conversation"):
            self.dialogue_manager.clear_session()
            self._respond("I've cleared the session context.", ResponseMode.CONFIRMATION)
            return
            
        if text.lower() in ("pause", "pause workflow", "wait a second"):
            self.workflow_service.pause()
            self._respond("I have paused the workflow.", ResponseMode.CONFIRMATION)
            return
            
        if text.lower() in ("continue", "resume", "resume workflow"):
            self._respond("Resuming execution.", ResponseMode.CONFIRMATION)
            self.workflow_service.resume()
            return
            
        if text.lower() in ("stop", "cancel", "cancel workflow"):
            self.workflow_service.cancel()
            self._respond("Workflow has been cancelled.", ResponseMode.CONFIRMATION)
            return
            
        norm_result = self.normalization_service.normalize_transcription(text)
        self.event_bus.publish(PipelineEventType.NORMALIZATION_FINISHED, {"text": norm_result.normalized_text})
        
        normalized_text = norm_result.normalized_text
        self.dialogue_manager.add_to_history("user", normalized_text)
        
        # --- Dialogue Manager Interception ---
        pending_clarification = self.dialogue_manager.get_pending_clarification()
        pending_confirmation = self.dialogue_manager.get_pending_confirmation()
        
        if pending_clarification:
            if self.dialogue_manager.check_cancellation(normalized_text):
                self.dialogue_manager.clear_pending_clarification()
                self._respond("Okay, I've cancelled that request.", ResponseMode.CONFIRMATION)
                return
                
            merged_text = self.dialogue_manager.merge_clarification(pending_clarification.original_text, normalized_text)
            if merged_text:
                logger.info(f"Dialogue Manager intercepted reply. Merged: '{merged_text}'")
                normalized_text = merged_text
                self.dialogue_manager.clear_pending_clarification()
            else:
                cancelled = self.dialogue_manager.increment_clarification_attempt()
                if cancelled:
                    self._respond("I'm still having trouble understanding. Let's start over.", ResponseMode.ERROR)
                else:
                    self._respond("I'm sorry, I still don't understand. Can you rephrase?", ResponseMode.WARNING)
                return
                
        elif pending_confirmation:
            clean_text = normalized_text.lower().strip('.!?')
            if self.dialogue_manager.check_cancellation(normalized_text) or clean_text in ("no", "n", "nope"):
                self.dialogue_manager.clear_pending_confirmation()
                self._respond("Action cancelled.", ResponseMode.CONFIRMATION)
                return
            elif clean_text in ("yes", "y", "do it", "sure", "ok", "confirm"):
                plan = pending_confirmation.plan
                self.dialogue_manager.clear_pending_confirmation()
                workflow = self.workflow_composer.compose([plan])
                self.workflow_service.execute_workflow(workflow)
                self._respond("Execution completed successfully.", ResponseMode.CONVERSATION)
                return
            else:
                self._respond("Please confirm with Yes or No.", ResponseMode.WARNING)
                return
        
        # 1. Task Decomposition
        atomic_tasks = self.task_decomposer.decompose(normalized_text)
        
        # 2. Intent Routing & LLM Planning (Sequential Data Gathering)
        automation_plans = []
        knowledge_requests = []
        conversation_responses = []
        fallback_responses = []
        
        for task in atomic_tasks:
            router_result = self.router_service.route_request(task.text)
            logger.info(f"ROUTED TASK '{task.text}' to DESTINATION: {router_result.destination} (INTENT: {router_result.intent.value})")
            self.event_bus.publish(PipelineEventType.INTENT_CLASSIFIED, {"intent": router_result.intent.value, "destination": router_result.destination})
            
            # Context Resolution happens AFTER Intent Classification
            resolved_text, conf = self.dialogue_manager.resolve_reference(task.text, router_result.intent.value)
            self.event_bus.publish(PipelineEventType.CONTEXT_RESOLVED, {"text": resolved_text, "confidence": conf})
            
            if conf < 0.60:
                self.dialogue_manager.set_pending_clarification(task.text, router_result.intent.value, "Ambiguous pronoun reference")
                self.event_bus.publish(PipelineEventType.CLARIFICATION_REQUESTED, {"reason": "Ambiguous reference. Please clarify."})
                fallback_responses.append("I'm not exactly sure what you're referring to. Could you be more specific?")
                continue
                
            router_result.normalized_text = resolved_text
            
            if router_result.destination == "Planner":
                self.event_bus.publish(PipelineEventType.PLANNER_STARTED)
                plan = self.llm_service.generate_plan(router_result.normalized_text)
                needs_confirm = self.safety_validator.validate_plan(plan)
                
                if needs_confirm:
                    self.dialogue_manager.set_pending_confirmation(plan, "This action requires manual confirmation.")
                    self.event_bus.publish(PipelineEventType.CONFIRMATION_REQUESTED, {"reason": "Are you sure you want to execute this action?"})
                    fallback_responses.append("This action requires manual confirmation. Are you sure?")
                else:
                    automation_plans.append(plan)
                    
            elif router_result.destination == "LLMChatService":
                history_str = self.dialogue_manager.get_history_string()
                knowledge_requests.append({"text": router_result.normalized_text, "history_str": history_str})
                
            elif router_result.destination == "ConversationService":
                history_str = self.dialogue_manager.get_history_string()
                response_text = self.conversation_service.respond(router_result.normalized_text, history_str)
                conversation_responses.append(response_text)
                
            else:
                if router_result.intent.value == "MIXED":
                    response_text = self.fallback_service.handle_mixed_intent()
                elif router_result.confidence < 0.60:
                    response_text = self.fallback_service.handle_low_confidence()
                else:
                    response_text = self.fallback_service.handle_unknown()
                fallback_responses.append(response_text)
                
        # 3. Workflow Assembly & Execution Planning
        graph = TaskGraph()
        
        prev_node_id = None
        for plan in automation_plans:
            logical_workflow = self.workflow_builder.build_workflow(request.text, plan)
            executable_workflow = self.execution_planner.plan_execution(logical_workflow)
            
            node = ExecutionNode(
                id=executable_workflow.workflow_id,
                handler_type="WorkflowHandler",
                payload=executable_workflow
            )
            graph.add_node(node)
            if prev_node_id:
                graph.add_dependency(node.id, prev_node_id)
            prev_node_id = node.id
            
        for kr in knowledge_requests:
            import uuid
            node = ExecutionNode(
                id=str(uuid.uuid4()),
                handler_type="KnowledgeHandler",
                payload=kr
            )
            graph.add_node(node)
        
        # 4. Concurrent Scheduling (Execution)
        summary = self.scheduler_engine.execute(graph)
        
        # 5. Response Aggregation
        final_text = self.response_aggregator.aggregate(summary.results, graph)
        
        merged_responses = []
        if conversation_responses:
            merged_responses.append(" ".join(conversation_responses))
        if final_text:
            merged_responses.append(final_text)
        if fallback_responses:
            merged_responses.append(" ".join(fallback_responses))
            
        final_response_text = " ".join(merged_responses).strip()
        if final_response_text:
            self._respond(final_response_text, ResponseMode.CONVERSATION)

    def _respond(self, text: str, mode: ResponseMode, profile: ResponseProfile = None):
        if not profile:
            profile = ResponseProfile(mode=mode, max_sentences=2)
        
        self.dialogue_manager.add_to_history("assistant", text)
        self.event_bus.publish(PipelineEventType.RESPONSE_GENERATED, {"text": text})
        
        formatted = self.response_formatter.format_response(text, profile)
        
        self.event_bus.publish(PipelineEventType.TTS_STARTED, {"formatted_text": formatted.formatted_text})
        self.tts_service.say(formatted.formatted_text)
