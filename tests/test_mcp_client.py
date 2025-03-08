#!/usr/bin/env python3
"""
Test script for Docker MCP server using a simple MCP client
"""

import os
import sys
import json
import subprocess
import time
import requests
from termcolor import colored

def print_test(message):
    """Print test message in cyan"""
    print(colored(f"[TEST] {message}", "cyan"))

def print_result(message):
    """Print result message in magenta"""
    print(colored(f"[RESULT] {message}", "magenta"))

def main():
    """Test MCP server using the MCP inspector/client"""
    try:
        # Start the MCP server in the background
        print_test("Starting the MCP server in the background...")
        server_process = subprocess.Popen(
            ["fastmcp", "dev", "src/main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for the server to start
        print_test("Waiting for the server to start...")
        time.sleep(5)
        
        # Now we can access the server API on the default port
        base_url = "http://localhost:8000"
        
        # Get server info
        print_test("Getting server info...")
        response = requests.get(f"{base_url}/info")
        if response.status_code == 200:
            print_result(f"Server info: {json.dumps(response.json(), indent=2)}")
        else:
            print(colored(f"[ERROR] Failed to get server info: {response.status_code}", "red"))
        
        # Test execute_code tool
        print_test("Testing execute_code tool...")
        code_payload = {
            "name": "execute_code",
            "arguments": {
                "language": "python",
                "code": "print('Hello from MCP client!')\nprint(2 + 2)"
            }
        }
        response = requests.post(f"{base_url}/tools/execute", json=code_payload)
        if response.status_code == 200:
            print_result(f"Code execution result: {json.dumps(response.json(), indent=2)}")
        else:
            print(colored(f"[ERROR] Failed to execute code: {response.status_code}", "red"))
        
        # Test list_supported_languages tool
        print_test("Testing list_supported_languages tool...")
        langs_payload = {
            "name": "list_supported_languages",
            "arguments": {}
        }
        response = requests.post(f"{base_url}/tools/execute", json=langs_payload)
        if response.status_code == 200:
            print_result(f"Supported languages: {json.dumps(response.json(), indent=2)}")
        else:
            print(colored(f"[ERROR] Failed to list languages: {response.status_code}", "red"))
        
        # Clean up - stop the server
        print_test("Stopping the MCP server...")
        server_process.terminate()
        stdout, stderr = server_process.communicate(timeout=5)
        
        print_test("All tests completed!")
        
    except Exception as e:
        print(colored(f"[ERROR] Test failed: {str(e)}", "red"))
        try:
            server_process.terminate()
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main() 