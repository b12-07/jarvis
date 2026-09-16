import os
import subprocess

def read_file(filepath: str) -> str:
    """Reads the content of a file from the local filesystem."""
    try:
        if not os.path.exists(filepath):
            return f"Error: File '{filepath}' does not exist."
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file '{filepath}': {e}"

def write_file(filepath: str, content: str) -> str:
    """Writes content to a file on the local filesystem. Creates or overwrites the file."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to '{filepath}'."
    except Exception as e:
        return f"Error writing to file '{filepath}': {e}"

def execute_command(command: str) -> str:
    """Executes a terminal/shell command on the local system and returns the standard output and standard error."""
    try:
        # Use shell=True for convenience, but capture output
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30 # Prevent hanging forever
        )

        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"

        if not output:
            output = f"Command executed successfully with exit code {result.returncode} (No output)."
        else:
            output += f"\nExit code: {result.returncode}"

        return output
    except subprocess.TimeoutExpired:
        return f"Error: Command '{command}' timed out after 30 seconds."
    except Exception as e:
        return f"Error executing command '{command}': {e}"
