#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
from fastmcp import FastMCP
from termcolor import colored
import sys
import os
import shlex  # Add shlex for proper command splitting
import json
import logging

# Set up logging to stderr for MCP compatibility
logging.basicConfig(
    level=logging.INFO,
    format="[DockerMCP] %(levelname)s: %(message)s",
    stream=sys.stderr
)

# CONSTANTS
SERVER_NAME = "DockerManager"

def print_colored(message, color="green", prefix="[DockerMCP]"):
    """Print colored messages to stderr for better compatibility with MCP protocol."""
    # Use stderr only to avoid interfering with stdout JSON communication
    print(colored(f"{prefix} {message}", color), file=sys.stderr)

# Create an MCP server instance
mcp = FastMCP(SERVER_NAME, disable_stdout_logging=True)

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
    logging.error("Docker is not available. Please make sure Docker is installed and running.")
    sys.exit(1)
except Exception as e:
    print_colored(f"Error checking Docker: {str(e)}", "red")
    logging.error(f"Error checking Docker: {str(e)}")
    sys.exit(1)

@mcp.tool()
def create_container(image: str, container_name: str, dependencies: str = "") -> str:
    """
    Create and start a Docker container with optional dependencies.
    
    Parameters:
    • image: The Docker image to use (e.g., "ubuntu:latest", "node:16", "python:3.9-slim").
    • container_name: A unique name for the container.
    • dependencies: Space-separated list of packages to install (e.g., "numpy pandas matplotlib" or "express lodash").
    
    This tool uses 'docker run' in detached mode with a command that keeps the container running.
    If dependencies are specified, they will be installed after the container starts.
    Automatically detects appropriate package manager (pip, npm, apt, apk) based on the image.
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
        
        # Install dependencies if specified
        if dependencies:
            print_colored(f"Installing dependencies: {dependencies}", "cyan")
            
            # Determine package manager based on image
            if "node" in image.lower() or "javascript" in image.lower():
                # For Node.js images, use npm
                print_colored("Detected Node.js image, using npm", "cyan")
                # First check if npm is available
                try:
                    npm_check = subprocess.run(
                        ["docker", "exec", container_name, "npm", "--version"],
                        capture_output=True, text=True, check=True, timeout=10
                    )
                    print_colored(f"npm version: {npm_check.stdout.strip()}", "cyan")
                    
                    # For npm, we'll install packages globally to avoid needing a package.json
                    install_cmd = f"npm install -g {dependencies}"
                except subprocess.CalledProcessError:
                    error_msg = "npm not found in container, defaulting to other package managers"
                    print_colored(error_msg, "yellow")
                    # Fall through to other package manager detection
            elif "python" in image.lower():
                # For Python images, use pip
                print_colored("Detected Python image, using pip", "cyan")
                install_cmd = f"pip install {dependencies}"
            elif any(distro in image.lower() for distro in ["ubuntu", "debian"]):
                # For Debian/Ubuntu images
                print_colored("Detected Debian/Ubuntu image, using apt-get", "cyan")
                install_cmd = f"apt-get update && apt-get install -y {dependencies}"
            elif "alpine" in image.lower():
                # For Alpine images
                print_colored("Detected Alpine image, using apk", "cyan")
                install_cmd = f"apk add --no-cache {dependencies}"
            else:
                # Default to pip for unknown images with a warning
                print_colored("Image type not recognized, attempting to detect available package managers", "yellow")
                
                # Try to detect available package managers
                package_managers = []
                
                # Check for npm
                try:
                    npm_check = subprocess.run(
                        ["docker", "exec", container_name, "npm", "--version"],
                        capture_output=True, text=True, check=False, timeout=5
                    )
                    if npm_check.returncode == 0:
                        package_managers.append("npm")
                except Exception:
                    pass
                
                # Check for pip
                try:
                    pip_check = subprocess.run(
                        ["docker", "exec", container_name, "pip", "--version"],
                        capture_output=True, text=True, check=False, timeout=5
                    )
                    if pip_check.returncode == 0:
                        package_managers.append("pip")
                except Exception:
                    pass
                
                # Choose package manager based on detection
                if "npm" in package_managers:
                    print_colored("npm found, using it for installation", "cyan")
                    install_cmd = f"npm install -g {dependencies}"
                elif "pip" in package_managers:
                    print_colored("pip found, using it for installation", "cyan")
                    install_cmd = f"pip install {dependencies}"
                else:
                    print_colored("No known package managers detected, defaulting to pip install", "yellow")
                    install_cmd = f"pip install {dependencies}"
            
            try:
                # Execute the installation command
                print_colored(f"Running: {install_cmd}", "cyan")
                install_result = subprocess.run(
                    ["docker", "exec", container_name, "sh", "-c", install_cmd],
                    capture_output=True, text=True, check=True, timeout=180  # Allow more time for installations
                )
                print_colored(f"Dependencies installed successfully", "green")
                return f"Container created with ID: {container_id}\nDependencies installed: {dependencies}"
            except subprocess.CalledProcessError as e:
                error_msg = f"Error installing dependencies: {e.stderr}"
                print_colored(error_msg, "red")
                return f"Container created with ID: {container_id}\n{error_msg}"
            except subprocess.TimeoutExpired:
                error_msg = "Timeout while installing dependencies. Operation took too long."
                print_colored(error_msg, "red")
                return f"Container created with ID: {container_id}\n{error_msg}"
            except Exception as e:
                error_msg = f"Unexpected error installing dependencies: {str(e)}"
                print_colored(error_msg, "red")
                return f"Container created with ID: {container_id}\n{error_msg}"
        
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

@mcp.tool()
def add_dependencies(container_name: str, dependencies: str) -> str:
    """
    Install additional dependencies in an existing Docker container.
    
    Parameters:
    • container_name: The name of the target container.
    • dependencies: Space-separated list of packages to install (e.g., "numpy pandas matplotlib" or "express lodash").
    
    This tool automatically detects the appropriate package manager (pip, npm, apt, apk)
    available in the container and uses it to install the specified dependencies.
    """
    print_colored(f"Adding dependencies to container '{container_name}': {dependencies}")
    
    try:
        # Check if container exists and is running
        container_check = subprocess.run(
            ["docker", "container", "inspect", "-f", "{{.State.Running}}", container_name],
            capture_output=True, text=True, check=True, timeout=10
        )
        
        if container_check.stdout.strip() != "true":
            error_msg = f"Container '{container_name}' is not running or does not exist"
            print_colored(error_msg, "red")
            return error_msg
        
        # Try to detect available package managers
        package_managers = []
        
        # Check for npm
        try:
            npm_check = subprocess.run(
                ["docker", "exec", container_name, "npm", "--version"],
                capture_output=True, text=True, check=False, timeout=5
            )
            if npm_check.returncode == 0:
                package_managers.append("npm")
                print_colored(f"Found npm: {npm_check.stdout.strip()}", "cyan")
        except Exception:
            pass
        
        # Check for pip
        try:
            pip_check = subprocess.run(
                ["docker", "exec", container_name, "pip", "--version"],
                capture_output=True, text=True, check=False, timeout=5
            )
            if pip_check.returncode == 0:
                package_managers.append("pip")
                print_colored(f"Found pip: {pip_check.stdout.strip()}", "cyan")
        except Exception:
            pass
        
        # Check for apt-get
        try:
            apt_check = subprocess.run(
                ["docker", "exec", container_name, "apt-get", "--version"],
                capture_output=True, text=True, check=False, timeout=5
            )
            if apt_check.returncode == 0:
                package_managers.append("apt-get")
                print_colored("Found apt-get", "cyan")
        except Exception:
            pass
        
        # Check for apk
        try:
            apk_check = subprocess.run(
                ["docker", "exec", container_name, "apk", "--version"],
                capture_output=True, text=True, check=False, timeout=5
            )
            if apk_check.returncode == 0:
                package_managers.append("apk")
                print_colored("Found apk", "cyan")
        except Exception:
            pass
        
        # Choose package manager based on detection
        if not package_managers:
            error_msg = "No supported package managers found in the container"
            print_colored(error_msg, "red")
            return error_msg
        
        print_colored(f"Available package managers: {', '.join(package_managers)}", "cyan")
        
        # Choose the appropriate package manager
        if "npm" in package_managers:
            print_colored("Using npm for installation", "cyan")
            install_cmd = f"npm install -g {dependencies}"
        elif "pip" in package_managers:
            print_colored("Using pip for installation", "cyan")
            install_cmd = f"pip install {dependencies}"
        elif "apt-get" in package_managers:
            print_colored("Using apt-get for installation", "cyan")
            install_cmd = f"apt-get update && apt-get install -y {dependencies}"
        elif "apk" in package_managers:
            print_colored("Using apk for installation", "cyan")
            install_cmd = f"apk add --no-cache {dependencies}"
        else:
            error_msg = "No supported package managers found in the container"
            print_colored(error_msg, "red")
            return error_msg
        
        # Execute the installation command
        print_colored(f"Running: {install_cmd}", "cyan")
        install_result = subprocess.run(
            ["docker", "exec", container_name, "sh", "-c", install_cmd],
            capture_output=True, text=True, check=True, timeout=180  # Allow more time for installations
        )
        
        print_colored("Dependencies installed successfully", "green")
        return f"Dependencies installed in container '{container_name}': {dependencies}"
    except subprocess.CalledProcessError as e:
        error_msg = f"Error installing dependencies: {e.stderr}"
        print_colored(error_msg, "red")
        return error_msg
    except subprocess.TimeoutExpired:
        error_msg = "Timeout while installing dependencies. Operation took too long."
        print_colored(error_msg, "red")
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print_colored(error_msg, "red")
        return error_msg

@mcp.tool()
def list_containers(show_all: bool = True) -> str:
    """
    List all Docker containers with their details.
    
    Parameters:
    • show_all: Whether to show all containers including stopped ones (default: True).
                If False, only shows running containers.
    
    Returns information about containers including ID, name, status, and image.
    """
    print_colored(f"Listing {'all' if show_all else 'running'} containers...")
    
    try:
        cmd = ["docker", "ps"]
        if show_all:
            cmd.append("-a")  # Show all containers, not just running ones
            
        # Add format to get consistent, parseable output with specific fields
        cmd.extend([
            "--format", 
            "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Image}}\t{{.RunningFor}}"
        ])
        
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, check=True, timeout=15
        )
        
        container_list = result.stdout.strip()
        
        if container_list and not container_list.startswith("CONTAINER ID"):
            # This means we have a table header but no data
            print_colored("No containers found", "yellow")
            return f"No {'existing' if show_all else 'running'} containers found."
        
        print_colored(f"Found containers:\n{container_list}", "cyan")
        
        # Add extra information about how to use this data
        usage_info = "\nYou can use these container names with other tools like add_dependencies, execute_code, etc."
        if show_all:
            usage_info += "\nNote: Only containers with 'Up' in their Status are currently running and can be interacted with."
        
        return f"{container_list}{usage_info}"
    except subprocess.CalledProcessError as e:
        error_msg = f"Error listing containers: {e.stderr}"
        print_colored(error_msg, "red")
        return error_msg
    except subprocess.TimeoutExpired:
        error_msg = "Timeout while listing containers. Operation took too long."
        print_colored(error_msg, "red")
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print_colored(error_msg, "red")
        return error_msg 

# Main entry point for MCP server
if __name__ == "__main__":
    print_colored("Starting MCP Docker Manager server...", "green")
    try:
        # This starts the MCP server
        mcp.run()
    except Exception as e:
        error_message = f"Error starting MCP server: {str(e)}"
        logging.error(error_message)
        print(error_message, file=sys.stderr)
        sys.exit(1) 