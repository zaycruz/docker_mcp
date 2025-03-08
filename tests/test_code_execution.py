#!/usr/bin/env python3
"""
Test script for Docker MCP server code execution
"""

import os
import sys
import json
from termcolor import colored

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Import our modules
from src.docker_execution.docker_manager import DockerManager
from src.docker_execution.code_executor import CodeExecutor

def print_test(message):
    """Print test message in cyan"""
    print(colored(f"[TEST] {message}", "cyan"))

def print_result(message):
    """Print result message in magenta"""
    print(colored(f"[RESULT] {message}", "magenta"))

def main():
    """Run tests for code execution"""
    try:
        print_test("Initializing Docker manager...")
        docker_manager = DockerManager()
        
        print_test("Initializing Code executor...")
        code_executor = CodeExecutor(docker_manager)
        
        # Test Python code execution
        print_test("Testing Python code execution...")
        python_code = """
print("Hello from Python!")
a = 5
b = 10
print(f"Sum: {a + b}")
"""
        result = code_executor.execute("python", python_code)
        print_result(f"Python execution result: {json.dumps(result, indent=2)}")
        
        # Test JavaScript code execution
        print_test("Testing JavaScript code execution...")
        js_code = """
console.log("Hello from JavaScript!");
const a = 5;
const b = 10;
console.log(`Sum: ${a + b}`);
"""
        result = code_executor.execute("javascript", js_code)
        print_result(f"JavaScript execution result: {json.dumps(result, indent=2)}")
        
        print_test("All tests completed!")
        
    except Exception as e:
        print(colored(f"[ERROR] Test failed: {str(e)}", "red"))
        sys.exit(1)

if __name__ == "__main__":
    main() 