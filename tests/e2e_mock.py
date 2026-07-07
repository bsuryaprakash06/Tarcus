import sys
import time
import os
import threading
from src.services.pipeline_worker import PipelineWorker
from src.models.input import InputRequest, InputSource
from src.utils.logger import get_logger

logger = get_logger("e2e_test")

def run_e2e():
    logger.info("Starting headless E2E test...")
    worker = PipelineWorker()
    worker.start()
    
    # Send a mock request
    request = InputRequest(
        request_id="test_req_001",
        text="Open Notepad and type Hello Shane",
        source=InputSource.TEXT
    )
    
    worker.session_manager.enqueue(request)
    logger.info("Request enqueued.")
    
    # Wait for completion
    timeout = 30
    start = time.time()
    
    while time.time() - start < timeout:
        time.sleep(1)
        
    worker.stop()
    worker.join(timeout=2)
    logger.info("E2E test finished.")
    
if __name__ == "__main__":
    run_e2e()
