# Docker MCP Server

A powerful Model Context Protocol (MCP) server that executes code in isolated Docker containers and returns the results to language models like Claude.

## Features

- **Isolated Code Execution**: Run code in Docker containers separated from your main system
- **Multi-language Support**: Execute code in any language with a Docker image
- **Complex Script Support**: Run both simple commands and complete multi-line scripts
- **Package Management**: Install dependencies using pip, npm, apt-get, or apk
- **Container Management**: Create, list, and clean up Docker containers easily
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

#### 1. List Containers

Lists all Docker containers and their details:

- **Parameters**:
  - `show_all`: (Optional) Whether to show all containers including stopped ones (default: True)

#### 2. Create Container

Creates and starts a Docker container with optional dependencies:

- **Parameters**:
  - `image`: The Docker image to use (e.g., "python:3.9-slim", "node:16")
  - `container_name`: A unique name for the container
  - `dependencies`: (Optional) Space-separated list of packages to install (e.g., "numpy pandas", "express lodash")

#### 3. Add Dependencies

Installs additional packages in an existing Docker container:

- **Parameters**:
  - `container_name`: The name of the target container
  - `dependencies`: Space-separated list of packages to install

#### 4. Execute Code

Executes a command inside a running Docker container:

- **Parameters**:
  - `container_name`: The name of the target container
  - `command`: The command to execute inside the container

#### 5. Execute Python Script

Executes a multi-line Python script inside a running Docker container:

- **Parameters**:
  - `container_name`: The name of the target container
  - `script_content`: The full Python script content
  - `script_args`: Optional arguments to pass to the script

#### 6. Cleanup Container

Stops and removes a Docker container:

- **Parameters**:
  - `container_name`: The name of the container to clean up

### Examples

#### Basic Workflow Example

```python
# 1. List existing containers to see what's already running
list_containers()

# 2. Create a new container
create_container(
    image="python:3.9-slim", 
    container_name="python-example", 
    dependencies="numpy pandas"
)

# 3. Execute a command in the container
execute_code(
    container_name="python-example", 
    command="python -c 'import numpy as np; print(\"NumPy version:\", np.__version__)'"
)

# 4. Add more dependencies later
add_dependencies(
    container_name="python-example", 
    dependencies="matplotlib scikit-learn"
)

# 5. List containers again to confirm status
list_containers(show_all=False)  # Only show running containers

# 6. Clean up when done
cleanup_container(container_name="python-example")
```

#### Python Data Analysis Example

```python
# 1. Create a container with dependencies
create_container(
    image="python:3.9-slim", 
    container_name="python-test", 
    dependencies="numpy pandas matplotlib"
)

# 2. Execute a Python script
script = """
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Create some data
data = pd.DataFrame({
    'x': np.random.randn(100),
    'y': np.random.randn(100)
})

print(f"Data shape: {data.shape}")
print(f"Data correlation: {data.corr().iloc[0,1]:.4f}")
"""
execute_python_script(container_name="python-test", script_content=script)

# 3. Add additional dependencies later if needed
add_dependencies(container_name="python-test", dependencies="scikit-learn")

# 4. Verify container is running
list_containers(show_all=False)

# 5. Clean up when done
cleanup_container(container_name="python-test")
```

#### Node.js Example

```python
# 1. Check for existing Node.js containers
list_containers()

# 2. Create a Node.js container
create_container(
    image="node:16", 
    container_name="node-test", 
    dependencies="express axios"
)

# 3. Execute a Node.js script
execute_code(
    container_name="node-test", 
    command="node -e \"console.log('Node.js version: ' + process.version); console.log('Express installed: ' + require.resolve('express'));\""
)

# 4. Add more dependencies
add_dependencies(container_name="node-test", dependencies="lodash moment")

# 5. Clean up when done
cleanup_container(container_name="node-test")
```

## Package Manager Support

The Docker MCP server automatically detects and uses the appropriate package manager:

- **Python containers**: Uses `pip`
- **Node.js containers**: Uses `npm`
- **Debian/Ubuntu containers**: Uses `apt-get`
- **Alpine containers**: Uses `apk`

For containers where the package manager isn't obvious from the image name, the server attempts to detect available package managers.

## Integrating with Claude and Other LLMs

This MCP server can be integrated with Claude and other LLMs that support the Model Context Protocol. Use the `fastmcp install` command to register it with Claude:

```bash
fastmcp install src/docker_mcp.py
```

## Troubleshooting

- **Port Already in Use**: If you see "Address already in use" errors, ensure no other MCP Inspector instances are running.
- **Docker Connection Issues**: Verify that Docker is running with `docker --version`.
- **Container Timeouts**: The server includes fallback mechanisms for containers that don't respond within expected timeframes.
- **Package Installation Failures**: Check that the package name is correct for the specified package manager.
- **No Containers Found**: If list_containers shows no results, Docker might not have any containers created yet.

## Security Considerations

This server executes code in Docker containers, which provides isolation from the host system. However, exercise caution:

- Don't expose this server publicly without additional security measures
- Be careful when mounting host volumes into containers
- Consider resource limits for containers to prevent DoS attacks

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 