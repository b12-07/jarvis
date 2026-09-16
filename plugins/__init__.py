import os
import importlib
import inspect

def load_all_plugins():
    """Scans the plugins directory and loads all callable functions intended as tools."""
    tools = []
    plugin_dir = os.path.dirname(__file__)

    for filename in os.listdir(plugin_dir):
        if filename.endswith(".py") and not filename.startswith("__") and filename != "core.py":
            module_name = f"plugins.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                # If module defines __tools__, use that list.
                # Otherwise, grab all public functions defined in that module.
                if hasattr(module, "__tools__"):
                    for func in module.__tools__:
                        tools.append(func)
                else:
                    for name, obj in inspect.getmembers(module, inspect.isfunction):
                        if obj.__module__ == module_name and not name.startswith("_"):
                            tools.append(obj)
            except Exception as e:
                print(f"Error loading plugin {module_name}: {e}")

    return tools
