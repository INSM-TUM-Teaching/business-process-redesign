import sys
import os

# Some workaround I found that ensures that modules like 'traces_to_matrix' can be found by tests
# regardless of how pytest is invoked or structured.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
