import os
import sys
import time
from src.services.pipeline_worker import PipelineWorker
from src.services.session_manager import SessionManager
from src.models.input import InputRequest, InputSource
import logging

logging.basicConfig(level=logging.DEBUG)

def run():
    print("Starting pipeline worker...")
    worker = PipelineWorker()
    worker.start()
    
    print("Enqueueing request...")
    sm = SessionManager()
    req = InputRequest(request_id="test_001", text="Open NotePad and Type Hello Shane", source=InputSource.TEXT)
    sm.enqueue(req)
    
    print("Waiting for processing (20s)...")
    time.sleep(20)
    
    print("Stopping worker...")
    worker.stop()
    worker.join()

if __name__ == "__main__":
    run()
