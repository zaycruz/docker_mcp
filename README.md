# Docker MCP Server

A powerful Model Context Protocol (MCP) server that executes code in isolated Docker containers and returns the results to language models like Claude.

## Features

- **Isolated Code Execution**: Run code in Docker containers separated from your main system
- **Multi-language Support**: Execute code in any language with a Docker image
- **Complex Script Support**: Run both simple commands and complete multi-line scripts
- **Robust Error Handling**: Graceful timeout management and fallback mechanisms
- **Colorful Output**: Clear, color-coded console feedback

## Requirements

- Python 3.9+ 
- Docker installed and running
- fastmcp library

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/docker_mcp_server.git
   cd docker_mcp_server
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the MCP Inspector

To test and explore the server's functionality:

```bash
python run_server.py
```

The MCP Inspector interface will open in your browser at http://localhost:5173.

### Available Tools

The Docker MCP server provides the following tools:

#### 1. Create Container

Creates and starts a Docker container:

- **Parameters**:
  - `image`: The Docker image to use (e.g., "python:3.9-slim")
  - `container_name`: A unique name for the container

#### 2. Execute Code

Executes a command inside a running Docker container:

- **Parameters**:
  - `container_name`: The name of the target container
  - `command`: The command to execute inside the container

#### 3. Execute Python Script

Executes a multi-line Python script inside a running Docker container:

- **Parameters**:
  - `container_name`: The name of the target container
  - `script_content`: The full Python script content
  - `script_args`: Optional arguments to pass to the script

#### 4. Cleanup Container

Stops and removes a Docker container:

- **Parameters**:
  - `container_name`: The name of the container to clean up

### Example: Running a Python Script

```python
# 1. Create a container
create_container(image="python:3.9-slim", container_name="python-test")

# 2. Execute a Python script
script = """
def fibonacci(n):
    sequence = [0, 1]
    for i in range(2, n):
        sequence.append(sequence[i-1] + sequence[i-2])
    return sequence

result = fibonacci(10)
print(f"Fibonacci sequence: {result}")
"""
execute_python_script(container_name="python-test", script_content=script)

# 3. Clean up when done
cleanup_container(container_name="python-test")
```

## Integrating with Claude and Other LLMs

This MCP server can be integrated with Claude and other LLMs that support the Model Context Protocol. Use the `fastmcp install` command to register it with Claude:

```bash
fastmcp install src/docker_mcp.py
```

## Troubleshooting

- **Port Already in Use**: If you see "Address already in use" errors, ensure no other MCP Inspector instances are running.
- **Docker Connection Issues**: Verify that Docker is running with `docker --version`.
- **Container Timeouts**: The server includes fallback mechanisms for containers that don't respond within expected timeframes.

## Security Considerations

This server executes code in Docker containers, which provides isolation from the host system. However, exercise caution:

- Don't expose this server publicly without additional security measures
- Be careful when mounting host volumes into containers
- Consider resource limits for containers to prevent DoS attacks

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 