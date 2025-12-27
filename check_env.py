import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

try:
    import fastapi
    print(f"FastAPI version: {fastapi.__version__}")
except ImportError:
    print("FastAPI not installed")

try:
    import pytest
    print(f"pytest version: {pytest.__version__}")
except ImportError:
    print("pytest not installed")
