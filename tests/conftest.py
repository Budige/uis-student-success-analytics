"""
Pytest configuration for UIS Student Success Analytics tests.
Ensures correct Python path regardless of where pytest is run from.
"""
import sys
from pathlib import Path

# Add project root to path so imports work from any directory
sys.path.insert(0, str(Path(__file__).parent.parent))
