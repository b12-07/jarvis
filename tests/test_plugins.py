import os
import json
from plugins.task_observer import record_learning, recall_learnings, _load_memory, MEMORY_FILE
from plugins.analytics import analyze_directory_structure, scaffold_project_structure
import pytest

# Cleanup memory file before and after tests
@pytest.fixture(autouse=True)
def cleanup_memory():
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
    yield
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)

def test_task_observer_memory():
    # Test recording
    result = record_learning("test_topic", "This is a test lesson.")
    assert "Successfully recorded" in result

    # Test reading underlying file
    mem = _load_memory()
    assert "test_topic" in mem["skills"]
    assert mem["skills"]["test_topic"][0]["lesson"] == "This is a test lesson."

    # Test recall
    recall_specific = recall_learnings("test_topic")
    assert "This is a test lesson." in recall_specific

    recall_all = recall_learnings("all")
    assert "test_topic" in recall_all

def test_analyze_directory_structure(tmpdir):
    # Setup test dir
    test_dir = tmpdir.mkdir("test_repo")
    test_dir.join("main.py").write("print('hello')")
    test_dir.mkdir("src").join("utils.py").write("def add(): pass")

    tree = analyze_directory_structure(str(test_dir))
    assert "test_repo" in tree
    assert "main.py" in tree
    assert "src" in tree
    assert "utils.py" in tree

def test_scaffold_project_structure(tmpdir):
    test_dir = str(tmpdir.mkdir("scaffold_test"))
    structure = {
        "src": {
            "app.py": "print('running')"
        },
        "README.md": "# Test"
    }

    result = scaffold_project_structure(test_dir, json.dumps(structure))
    assert "Scaffolding complete" in result

    assert os.path.exists(os.path.join(test_dir, "README.md"))
    assert os.path.exists(os.path.join(test_dir, "src", "app.py"))

    with open(os.path.join(test_dir, "src", "app.py"), "r") as f:
        assert f.read() == "print('running')"
