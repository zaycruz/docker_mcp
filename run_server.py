#!/usr/bin/env python
# -*- coding: utf-8 -*-

from termcolor import colored
import subprocess
import sys
import os
import socket
import argparse

def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Docker MCP Server Runner')
    parser.add_argument('--direct', action='store_true',
                      help='Run the server directly without the MCP Inspector')
    parser.add_argument('--port', type=int, default=3000,
                      help='Port to run the server on (default: 3000)')
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_arguments()
    
    if args.direct:
        # Run the server directly without MCP Inspector
        print(colored("[DockerMCP] Starting Docker MCP server in direct mode...", "cyan"))
        print(colored(f"[DockerMCP] Server will run on port {args.port}", "cyan"))
        
        try:
            # Set the MCP_PORT environment variable
            os.environ["MCP_PORT"] = str(args.port)
            
            # Use fastmcp run instead of direct Python execution
            subprocess.run(["fastmcp", "run", "src/docker_mcp.py:mcp"], check=True)
        except KeyboardInterrupt:
            print(colored("[DockerMCP] Server shutdown requested. Exiting...", "yellow"))
            sys.exit(0)
        except Exception as e:
            print(colored(f"[DockerMCP] Error running server: {str(e)}", "red"))
            sys.exit(1)
    else:
        # Run with the MCP Inspector
        print(colored("[DockerMCP] Starting Docker MCP server with MCP Inspector...", "cyan"))
        
        # Check if common MCP Inspector ports are in use
        server_port = 3000
        client_port = 5173
        
        if is_port_in_use(server_port):
            print(colored(f"[DockerMCP] Warning: Port {server_port} (MCP server) is already in use.", "yellow"))
            print(colored("[DockerMCP] You may need to stop other running MCP servers or services using this port.", "yellow"))
        
        if is_port_in_use(client_port):
            print(colored(f"[DockerMCP] Warning: Port {client_port} (MCP Inspector client) is already in use.", "yellow")) 
            print(colored("[DockerMCP] You may need to stop other running MCP Inspector instances.", "yellow"))
        
        try:
            # Run the fastmcp dev command
            print(colored("[DockerMCP] Attempting to start MCP server with Docker tools...", "cyan"))
            subprocess.run(["fastmcp", "dev", "src/docker_mcp.py"], check=True)
        except KeyboardInterrupt:
            print(colored("[DockerMCP] Server shutdown requested. Exiting...", "yellow"))
            sys.exit(0)
        except subprocess.CalledProcessError as e:
            if "EADDRINUSE" in str(e):
                print(colored("[DockerMCP] ERROR: Port already in use. Please try the following:", "red"))
                print(colored("  1. Check for other running processes on ports 3000 and 5173", "yellow"))
                print(colored("  2. Stop those processes and try again", "yellow"))
                print(colored("  3. Or use the direct server approach:", "yellow"))
                print(colored("     python3 run_server.py --direct", "yellow"))
                print(colored("\nTo find and kill processes using these ports:", "cyan"))
                print(colored("  lsof -i :3000    # Find process on port 3000", "yellow"))
                print(colored("  lsof -i :5173    # Find process on port 5173", "yellow"))
                print(colored("  kill -9 <PID>    # Kill the process by ID", "yellow"))
            else:
                print(colored(f"[DockerMCP] Error running server: {str(e)}", "red"))
            sys.exit(1)
        except Exception as e:
            print(colored(f"[DockerMCP] Error running server: {str(e)}", "red"))
            sys.exit(1) 