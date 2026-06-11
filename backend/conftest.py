"""
backend/conftest.py — root-level pytest plugin (loaded before all other conftest files).

Injects the backend directory into sys.path at the very start of the pytest
process so that `from app.services import ...` works regardless of which Python
interpreter pytest was launched with.
"""
import sys
import os

# Resolve backend/ dir (the directory containing this file)
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
