#!/usr/bin/env python3
"""
Quick start script for Travel AI Assistant.
Runs the main CLI application.
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run main
from scripts.main import main

if __name__ == "__main__":
    main()
