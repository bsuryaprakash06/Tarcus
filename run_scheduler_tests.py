import sys
import traceback
from tests.test_scheduler import test_dag_dependency_ordering, test_resource_locks_exclusive

try:
    print("Testing DAG Dependency Ordering...")
    test_dag_dependency_ordering()
    print("[PASS] DAG Dependency Ordering\n")
    
    print("Testing Resource Locks Exclusive...")
    test_resource_locks_exclusive()
    print("[PASS] Resource Locks Exclusive\n")
    
    print("ALL TESTS PASSED!")
except Exception as e:
    print("TEST FAILED!")
    traceback.print_exc()
    sys.exit(1)
