import os

def analyze_directory_structure(path: str = ".") -> str:
    """
    Returns a tree-like string representation of the directory structure starting from the given path.
    Useful for understanding the codebase infrastructure before making changes or analyzing projects.
    """
    if not os.path.exists(path):
        return f"Error: Path '{path}' does not exist."

    tree = []

    # Simple recursive function to build the tree, ignoring hidden folders like .git
    def build_tree(current_path, prefix=""):
        try:
            items = sorted(os.listdir(current_path))
            items = [i for i in items if not i.startswith(".")] # ignore hidden

            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                item_path = os.path.join(current_path, item)

                connector = "└── " if is_last else "├── "
                tree.append(f"{prefix}{connector}{item}")

                if os.path.isdir(item_path):
                    extension = "    " if is_last else "│   "
                    build_tree(item_path, prefix + extension)
        except PermissionError:
            tree.append(f"{prefix}└── [Permission Denied]")

    tree.append(os.path.basename(os.path.abspath(path)) or path)
    build_tree(path)

    # Cap output if it's way too huge for LLM context
    result = "\n".join(tree)
    if len(result) > 10000:
        return result[:10000] + "\n... (truncated due to length)"
    return result

def scaffold_project_structure(base_path: str, structure_json_str: str) -> str:
    """
    Given a JSON string representing a directory/file structure, creates those files and folders on disk.
    Format example: '{"src": {"main.py": "print('hello')", "utils": {}}, "README.md": "# Title"}'
    """
    import json
    try:
        structure = json.loads(structure_json_str)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON format: {e}"

    log = []

    def create_structure(current_path, current_dict):
        for name, content in current_dict.items():
            target_path = os.path.join(current_path, name)
            if isinstance(content, dict):
                # It's a directory
                os.makedirs(target_path, exist_ok=True)
                log.append(f"Created directory: {target_path}")
                create_structure(target_path, content)
            elif isinstance(content, str):
                # It's a file
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(content)
                log.append(f"Created file: {target_path}")

    try:
        create_structure(base_path, structure)
        return "Scaffolding complete:\n" + "\n".join(log)
    except Exception as e:
        return f"Error during scaffolding: {e}"

__tools__ = [analyze_directory_structure, scaffold_project_structure]
