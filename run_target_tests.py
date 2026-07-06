import sys
import traceback
from tests.test_target import test_target_registry_lifecycle, test_target_resolver

try:
    print("Testing Target Registry Lifecycle...")
    test_target_registry_lifecycle()
    print("[PASS] Target Registry Lifecycle\n")
    
    print("Testing Target Resolver...")
    test_target_resolver()
    print("[PASS] Target Resolver\n")
    
    print("ALL TESTS PASSED!")
except Exception as e:
    print("TEST FAILED!")
    traceback.print_exc()
    sys.exit(1)
