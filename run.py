#!/usr/bin/env python3
"""
Simple script to run the Business Process Redesign Tool
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the Flask app
from app import app

if __name__ == "__main__":
    print("Starting Business Process Redesign Tool...")
    print("pen your browser to: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)

    app.run(debug=True, host="127.0.0.1", port=5000)
