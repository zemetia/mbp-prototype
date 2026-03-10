import sys
import traceback

try:
    with open('pytest_err.log', 'w') as f:
        try:
            import test_new_architecture
        except Exception as e:
            traceback.print_exc(file=f)
except Exception:
    pass
