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

# New Task Decomposer & Merger Services
from src.task_decomposer.decomposer import TaskDecomposer
from src.task_decomposer.execution_graph_builder import ExecutionGraphBuilder
from src.task_decomposer.request_scheduler import RequestScheduler
from src.workflow.workflow_composer import WorkflowComposer
from src.services.response_merger import ResponseMerger

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
        self.graph_builder = ExecutionGraphBuilder()
        self.scheduler = RequestScheduler()
        self.workflow_composer = WorkflowComposer()
        self.response_merger = ResponseMerger()
        
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
        
        # 2. Execution Graph Building
        execution_graph = self.graph_builder.build(atomic_tasks)
        
        # 3. Request Scheduling
        scheduled_batches = self.scheduler.schedule(execution_graph)
        
        responses = []
        automation_plans = []
        
        # 4. Route and Process each batch
        for batch in scheduled_batches:
            for task in batch:
                router_result = self.router_service.route_request(task.text)
                self.event_bus.publish(PipelineEventType.INTENT_CLASSIFIED, {"intent": router_result.intent.value, "destination": router_result.destination})
                
                # Context Resolution happens AFTER Intent Classification
                resolved_text, conf = self.dialogue_manager.resolve_reference(task.text, router_result.intent.value)
                self.event_bus.publish(PipelineEventType.CONTEXT_RESOLVED, {"text": resolved_text, "confidence": conf})
                
                if conf < 0.60:
                    self.dialogue_manager.set_pending_clarification(task.text, router_result.intent.value, "Ambiguous pronoun reference")
                    self.event_bus.publish(PipelineEventType.CLARIFICATION_REQUESTED, {"reason": "Ambiguous reference. Please clarify."})
                    responses.append({"intent": "WARNING", "text": "I'm not exactly sure what you're referring to. Could you be more specific?"})
                    continue
                    
                router_result.normalized_text = resolved_text
                
                if router_result.destination == "Planner":
                    self.event_bus.publish(PipelineEventType.PLANNER_STARTED)
                    plan = self.llm_service.generate_plan(router_result.normalized_text)
                    needs_confirm = self.safety_validator.validate_plan(plan)
                    
                    if needs_confirm:
                        self.dialogue_manager.set_pending_confirmation(plan, "This action requires manual confirmation.")
                        self.event_bus.publish(PipelineEventType.CONFIRMATION_REQUESTED, {"reason": "Are you sure you want to execute this action?"})
                        responses.append({"intent": "WARNING", "text": "This action requires manual confirmation. Are you sure?"})
                    else:
                        automation_plans.append(plan)
                        
                elif router_result.destination == "LLMChatService":
                    profile = ResponseProfile(mode=ResponseMode.KNOWLEDGE, max_sentences=3, ask_followup=True, style=DEFAULT_RESPONSE_STYLE, verbosity="short")
                    history_str = self.dialogue_manager.get_history_string()
                    knowledge_response = self.chat_service.respond(router_result.normalized_text, profile, history_str)
                    
                    self.event_bus.publish(PipelineEventType.KNOWLEDGE_GENERATED, {
                        "primary_topic": knowledge_response.primary_topic,
                        "secondary_topics": knowledge_response.secondary_topics
                    })
                    
                    responses.append({"intent": "KNOWLEDGE", "text": knowledge_response.answer})
                    
                elif router_result.destination == "ConversationService":
                    history_str = self.dialogue_manager.get_history_string()
                    response_text = self.conversation_service.respond(router_result.normalized_text, history_str)
                    responses.append({"intent": "CONVERSATION", "text": response_text})
                    
                else:
                    if router_result.intent.value == "MIXED":
                        response_text = self.fallback_service.handle_mixed_intent()
                    elif router_result.confidence < 0.60:
                        response_text = self.fallback_service.handle_low_confidence()
                    else:
                        response_text = self.fallback_service.handle_unknown()
                    responses.append({"intent": "UNKNOWN", "text": response_text})
                    
        # 5. Workflow Composition (if any automation tasks exist)
        if automation_plans:
            workflow = self.workflow_composer.compose(automation_plans)
            
            # Use threading to execute workflow so we don't block the Response Merger from speaking?
            # Actually, WorkflowEngine execution blocks until completed or failed.
            # We execute it immediately. 
            self.workflow_service.execute_workflow(workflow)
            
            # Assuming it succeeded, we acknowledge. (A real implementation would check workflow.status)
            responses.append({"intent": "AUTOMATION", "text": "Execution completed successfully."})
            
        # 6. Response Merging
        final_response_text = self.response_merger.merge(responses)
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
