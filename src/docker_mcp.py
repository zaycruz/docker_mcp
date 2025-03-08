#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
from fastmcp import FastMCP
from termcolor import colored
import sys
import os
import shlex  # Add shlex for proper command splitting

# CONSTANTS
SERVER_NAME = "DockerManager"

def print_colored(message, color="green", prefix="[DockerMCP]"):
    """Print colored messages for better visibility."""
    print(colored(f"{prefix} {message}", color))

# Create an MCP server instance
mcp = FastMCP(SERVER_NAME)

# When the server starts, check if Docker is available
try:
    docker_check = subprocess.run(
        ["docker", "--version"], 
        capture_output=True, 
        text=True
    )
    print_colored(f"Docker version: {docker_check.stdout.strip()}", "cyan")
except subprocess.SubprocessError:
    print_colored("Docker is not available. Please make sure Docker is installed and running.", "red")
    sys.exit(1)
except Exception as e:
    print_colored(f"Error checking Docker: {str(e)}", "red")
    sys.exit(1)

@mcp.tool()
def create_container(image: str, container_name: str) -> str:
    """
    Create and start a Docker container.
    
    Parameters:
    • image: The Docker image to use (e.g., "ubuntu:latest").
    • container_name: A unique name for the container.
    
    This tool uses 'docker run' in detached mode with a command that keeps the container running.
    """
    print_colored(f"Creating container with name '{container_name}' from image '{image}'...")
    
    try:
        # Start the container in detached mode with an infinite sleep to keep it running.
        result = subprocess.run(
            ["docker", "run", "-d", "--name", container_name, image, "sleep", "infinity"],
            capture_output=True, text=True, check=True, timeout=30
        )
        container_id = result.stdout.strip()
        print_colored(f"Container created successfully. ID: {container_id}")
        return f"Container created with ID: {container_id}"
    except subprocess.CalledProcessError as e:
        error_msg = f"Error creating container: {e.stderr}"
        print_colored(error_msg, "red")
        return error_msg
    except subprocess.TimeoutExpired:
        error_msg = "Timeout while creating container. Operation took too long."
        print_colored(error_msg, "red")
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print_colored(error_msg, "red")
        return error_msg

@mcp.tool()
def execute_code(container_name: str, command: str) -> str:
    """
    Execute a command inside a running Docker container.
    
    Parameters:
    • container_name: The name of the target container.
    • command: The command to execute inside the container.
    
    This tool uses 'docker exec' to run the command and returns the output.
    """
    print_colored(f"Executing command in container '{container_name}': {command}")
    
    try:
        # Check if this is a python -c command
        if command.startswith("python -c"):
            # For python -c commands, keep the entire string after -c as a single argument
            prefix, python_code = command.split("-c", 1)
            cmd_parts = ["python", "-c", python_code.strip()]
            print_colored(f"Detected Python code execution: {cmd_parts}", "cyan")
        else:
            # For other commands, use proper shell-like splitting
            cmd_parts = shlex.split(command)
            
        # Execute the command
        result = subprocess.run(
            ["docker", "exec", container_name] + cmd_parts,
            capture_output=True, text=True, check=True, timeout=30
        )
        print_colored(f"Command executed successfully")
        return f"Command output: {result.stdout}"
    except subprocess.CalledProcessError as e:
        error_msg = f"Error executing command: {e.stderr}"
        print_colored(error_msg, "red")
        return error_msg
    except subprocess.TimeoutExpired:
        error_msg = "Timeout while executing command. Operation took too long."
        print_colored(error_msg, "red")
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print_colored(error_msg, "red")
        return error_msg

@mcp.tool()
def execute_python_script(container_name: str, script_content: str, script_args: str = "") -> str:
    """
    Execute a Python script inside a running Docker container.
    
    Parameters:
    • container_name: The name of the target container.
    • script_content: The full Python script content to execute.
    • script_args: Optional arguments to pass to the script (default: "").
    
    This tool writes the script to a file in the container and executes it.
    """
    print_colored(f"Executing Python script in container '{container_name}'")
    script_path = "/tmp/script.py"
    
    try:
        # Write the script content to a file in the container
        print_colored("Writing Python script to container...", "cyan")
        # Escape single quotes in the script content
        escaped_content = script_content.replace("'", "'\\''")
        
        write_result = subprocess.run(
            ["docker", "exec", container_name, "bash", "-c", f"echo '{escaped_content}' > {script_path} && chmod +x {script_path}"],
            capture_output=True, text=True, check=True, timeout=30
        )
        
        # Execute the script
        print_colored(f"Running Python script: {script_path} {script_args}", "cyan")
        cmd_parts = ["python", script_path]
        if script_args:
            cmd_parts.extend(shlex.split(script_args))
            
        result = subprocess.run(
            ["docker", "exec", container_name] + cmd_parts,
            capture_output=True, text=True, check=True, timeout=60  # Allow more time for script execution
        )
        
        print_colored("Python script executed successfully")
        return f"Command output: {result.stdout}"
    except subprocess.CalledProcessError as e:
        error_msg = f"Error executing Python script: {e.stderr}"
        print_colored(error_msg, "red")
        return error_msg
    except subprocess.TimeoutExpired:
        error_msg = "Timeout while executing Python script. Operation took too long."
        print_colored(error_msg, "red")
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print_colored(error_msg, "red")
        return error_msg

@mcp.tool()
def cleanup_container(container_name: str) -> str:
    """
    Stop and remove a Docker container.
    
    Parameters:
    • container_name: The name of the container to stop and remove.
    
    This tool uses 'docker stop' followed by 'docker rm' to clean up the container.
    """
    print_colored(f"Cleaning up container '{container_name}'...")
    
    try:
        # Stop the container with a shorter timeout (5 seconds instead of default 10)
        print_colored(f"Stopping container '{container_name}'...", "yellow")
        stop_result = subprocess.run(
            ["docker", "stop", "--time", "5", container_name],
            capture_output=True, text=True, check=True, timeout=10
        )
        
        # Remove the container
        print_colored(f"Removing container '{container_name}'...", "yellow")
        rm_result = subprocess.run(
            ["docker", "rm", container_name],
            capture_output=True, text=True, check=True, timeout=10
        )
        
        print_colored(f"Container '{container_name}' has been successfully stopped and removed.")
        return f"Container '{container_name}' has been stopped and removed."
    except subprocess.CalledProcessError as e:
        error_msg = f"Error cleaning the container: {e.stderr}"
        print_colored(error_msg, "red")
        
        # If stop fails, try to force kill the container
        try:
            print_colored(f"Attempting to force kill container '{container_name}'...", "yellow")
            kill_result = subprocess.run(
                ["docker", "kill", container_name],
                capture_output=True, text=True, check=False, timeout=5
            )
            rm_result = subprocess.run(
                ["docker", "rm", "-f", container_name],
                capture_output=True, text=True, check=False, timeout=5
            )
            if rm_result.returncode == 0:
                print_colored(f"Container '{container_name}' has been forcibly removed.")
                return f"Container '{container_name}' has been forcibly removed after timeout."
        except Exception:
            pass
        
        return error_msg
    except subprocess.TimeoutExpired:
        error_msg = "Timeout while cleaning up container. Attempting to force remove..."
        print_colored(error_msg, "yellow")
        
        # If timeout occurs, try to force remove the container
        try:
            kill_result = subprocess.run(
                ["docker", "kill", container_name],
                capture_output=True, text=True, check=False, timeout=5
            )
            rm_result = subprocess.run(
                ["docker", "rm", "-f", container_name],
                capture_output=True, text=True, check=False, timeout=5
            )
            if rm_result.returncode == 0:
                print_colored(f"Container '{container_name}' has been forcibly removed after timeout.")
                return f"Container '{container_name}' has been forcibly removed after timeout."
            else:
                return "Failed to clean up container after timeout."
        except Exception as e:
            return f"Failed to force remove container: {str(e)}"
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print_colored(error_msg, "red")
        return error_msg 