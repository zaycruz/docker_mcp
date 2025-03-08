#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import subprocess
import time
import uuid
import sys
from termcolor import colored

class DockerMCPTests(unittest.TestCase):
    """Tests for Docker MCP server functionality."""

    def setUp(self):
        """Set up test environment by defining test container name."""
        # Generate a unique container name for this test run
        self.container_name = f"test-container-{uuid.uuid4().hex[:8]}"
        self.test_image = "alpine:latest"
        print(colored(f"[TEST] Using container name: {self.container_name}", "cyan"))
        
        # Check if Docker is available
        try:
            subprocess.run(
                ["docker", "--version"], 
                check=True, 
                capture_output=True, 
                text=True
            )
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            self.fail(f"Docker is not available. Please make sure Docker is installed and running: {str(e)}")

    def tearDown(self):
        """Clean up any containers that might be left over."""
        try:
            # Try to stop and remove the container used in tests
            subprocess.run(
                ["docker", "stop", self.container_name],
                capture_output=True, check=False
            )
            subprocess.run(
                ["docker", "rm", self.container_name],
                capture_output=True, check=False
            )
            print(colored(f"[TEST] Cleanup complete for container: {self.container_name}", "green"))
        except Exception as e:
            print(colored(f"[TEST] Cleanup error (this is usually fine): {str(e)}", "yellow"))

    def test_container_lifecycle(self):
        """Test full container lifecycle: create, execute, cleanup."""
        print(colored("\n[TEST] Testing container lifecycle...", "cyan"))
        
        # 1. Create container
        print(colored("[TEST] Creating container...", "blue"))
        try:
            create_result = subprocess.run(
                ["docker", "run", "-d", "--name", self.container_name, self.test_image, "sleep", "infinity"],
                capture_output=True, text=True, check=True
            )
            container_id = create_result.stdout.strip()
            print(colored(f"[TEST] Container created. ID: {container_id}", "green"))
        except subprocess.CalledProcessError as e:
            self.fail(f"Failed to create container: {e.stderr}")
        
        # Wait briefly to ensure container is running
        time.sleep(1)
        
        # 2. Execute command in container
        print(colored("[TEST] Executing command in container...", "blue"))
        try:
            exec_result = subprocess.run(
                ["docker", "exec", self.container_name, "echo", "Hello from Docker!"],
                capture_output=True, text=True, check=True
            )
            output = exec_result.stdout.strip()
            print(colored(f"[TEST] Command output: {output}", "green"))
            
            # Verify the command execution was successful
            self.assertEqual(output, "Hello from Docker!")
        except subprocess.CalledProcessError as e:
            self.fail(f"Failed to execute command in container: {e.stderr}")
        
        # 3. Cleanup container
        print(colored("[TEST] Cleaning up container...", "blue"))
        
        try:
            # Stop the container
            stop_result = subprocess.run(
                ["docker", "stop", self.container_name],
                capture_output=True, text=True, check=True
            )
            
            # Remove the container
            rm_result = subprocess.run(
                ["docker", "rm", self.container_name],
                capture_output=True, text=True, check=True
            )
            
            print(colored(f"[TEST] Container {self.container_name} stopped and removed", "green"))
            
            # Verify container no longer exists
            check_result = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"name={self.container_name}", "--format", "{{.Names}}"],
                capture_output=True, text=True, check=True
            )
            self.assertEqual(check_result.stdout.strip(), "")
            print(colored("[TEST] Verified container no longer exists", "green"))
        except subprocess.CalledProcessError as e:
            self.fail(f"Failed to cleanup container: {e.stderr}")

if __name__ == "__main__":
    print(colored("[TEST] Starting Docker MCP tests...", "cyan"))
    unittest.main() 