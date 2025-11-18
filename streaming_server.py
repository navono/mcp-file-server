import os
import json
from typing import Dict, Any, List

import anyio
import uvicorn
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server for streaming transport on port 8001
# Listen on 0.0.0.0 to accept connections from outside the container
mcp = FastMCP("file-server-streaming", host="0.0.0.0", port=8001)

# Set the base directory where we'll read and write files
BASE_DIR = "/data"  # This will be mapped to your local directory in Docker
MAX_INLINE_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
CHUNK_SIZE = 64 * 1024  # 64 KB per chunk


@mcp.tool()
async def list_files(path: str = "") -> str:
    """List all files in the specified directory.

    Args:
        path: Optional subdirectory path relative to the base directory
    """
    target_dir = os.path.normpath(os.path.join(BASE_DIR, path))

    # Security check to prevent directory traversal
    if not target_dir.startswith(BASE_DIR):
        return "Error: Cannot access directories outside of the base directory."

    try:
        files = os.listdir(target_dir)
        file_info: List[Dict[str, Any]] = []

        for file in files:
            full_path = os.path.join(target_dir, file)
            is_dir = os.path.isdir(full_path)
            size = os.path.getsize(full_path) if not is_dir else "-"
            file_type = "Directory" if is_dir else "File"

            file_info.append({
                "name": file,
                "type": file_type,
                "size": size,
            })

        return json.dumps(file_info, indent=2)
    except Exception as e:  # noqa: BLE001
        return f"Error listing files: {str(e)}"


@mcp.tool()
async def read_file(file_path: str) -> str:
    """Read the contents of a file.

    Args:
        file_path: Path to the file relative to the base directory
    """
    target_file = os.path.normpath(os.path.join(BASE_DIR, file_path))

    # Security check to prevent directory traversal
    if not target_file.startswith(BASE_DIR):
        return "Error: Cannot access files outside of the base directory."

    try:
        if not os.path.isfile(target_file):
            return f"Error: File does not exist or is not a file: {file_path}"

        file_size = os.path.getsize(target_file)
        if file_size > MAX_INLINE_FILE_SIZE:
            return (
                f"Error: File is too large to read inline "
                f"({file_size} bytes > {MAX_INLINE_FILE_SIZE} bytes). "
                "Please use read_file_chunk for streaming access."
            )

        with open(target_file, "r") as f:
            content = f.read()

        return content
    except Exception as e:  # noqa: BLE001
        return f"Error reading file: {str(e)}"


@mcp.tool()
async def read_file_chunk(
    file_path: str, offset: int = 0, length: int = CHUNK_SIZE
) -> str:
    """Read a chunk of a file starting from the given byte offset.

    Args:
        file_path: Path to the file relative to the base directory
        offset: Byte offset to start reading from
        length: Maximum number of bytes to read
    """
    target_file = os.path.normpath(os.path.join(BASE_DIR, file_path))

    # Security check to prevent directory traversal
    if not target_file.startswith(BASE_DIR):
        return "Error: Cannot access files outside of the base directory."

    try:
        if not os.path.isfile(target_file):
            return f"Error: File does not exist or is not a file: {file_path}"

        file_size = os.path.getsize(target_file)
        if offset < 0 or offset > file_size:
            return f"Error: Invalid offset {offset} for file of size {file_size}."

        # Normalise length to a sane range
        if length <= 0 or length > CHUNK_SIZE:
            length = CHUNK_SIZE

        with open(target_file, "rb") as f:
            f.seek(offset)
            data = f.read(length)

        next_offset = offset + len(data)
        done = next_offset >= file_size

        return json.dumps(
            {
                "file_path": file_path,
                "offset": offset,
                "next_offset": next_offset,
                "done": done,
                "file_size": file_size,
                "content": data.decode("utf-8", errors="replace"),
            },
            ensure_ascii=False,
        )
    except Exception as e:  # noqa: BLE001
        return f"Error reading file chunk: {str(e)}"


@mcp.tool()
async def write_file(file_path: str, content: str) -> str:
    """Write content to a file.

    Args:
        file_path: Path to the file relative to the base directory
        content: Content to write to the file
    """
    target_file = os.path.normpath(os.path.join(BASE_DIR, file_path))

    # Security check to prevent directory traversal
    if not target_file.startswith(BASE_DIR):
        return "Error: Cannot access files outside of the base directory."

    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(target_file), exist_ok=True)

        with open(target_file, "w") as f:
            f.write(content)

        return f"Successfully wrote to {file_path}"
    except Exception as e:  # noqa: BLE001
        return f"Error writing to file: {str(e)}"


@mcp.tool()
async def delete_file(file_path: str) -> str:
    """Delete a file.

    Args:
        file_path: Path to the file relative to the base directory
    """
    target_file = os.path.normpath(os.path.join(BASE_DIR, file_path))

    # Security check to prevent directory traversal
    if not target_file.startswith(BASE_DIR):
        return "Error: Cannot access files outside of the base directory."

    try:
        if not os.path.exists(target_file):
            return f"Error: File does not exist: {file_path}"

        if os.path.isdir(target_file):
            os.rmdir(target_file)
            return f"Successfully deleted directory: {file_path}"

        os.remove(target_file)
        return f"Successfully deleted file: {file_path}"
    except Exception as e:  # noqa: BLE001
        return f"Error deleting file: {str(e)}"


if __name__ == "__main__":

    async def _run_streamable_http() -> None:
        app = mcp.streamable_http_app()
        config = uvicorn.Config(
            app,
            host=mcp.settings.host,
            port=mcp.settings.port,
            log_level=mcp.settings.log_level.lower(),
            timeout_graceful_shutdown=0,
            timeout_keep_alive=0,
        )
        server = uvicorn.Server(config)
        await server.serve()

    try:
        anyio.run(_run_streamable_http)
    except KeyboardInterrupt:
        # Fast exit on Ctrl+C in local development
        pass
