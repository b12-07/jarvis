import os
import json
from datetime import datetime

MEMORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory", "skills_db.json")

def _load_memory() -> dict:
    if not os.path.exists(MEMORY_FILE):
        return {"skills": {}, "observations": []}
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"skills": {}, "observations": []}

def _save_memory(data: dict):
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def record_learning(topic: str, lesson: str) -> str:
    """
    Saves a new skill, principle, or observation to long-term memory.
    Use this when you solve a hard problem, fix a bug, or learn a user preference.
    """
    mem = _load_memory()
    timestamp = datetime.now().isoformat()

    if topic not in mem["skills"]:
        mem["skills"][topic] = []

    entry = {
        "timestamp": timestamp,
        "lesson": lesson
    }
    mem["skills"][topic].append(entry)
    mem["observations"].append(f"[{timestamp}] Learned about {topic}: {lesson}")

    _save_memory(mem)
    return f"Successfully recorded learning under topic '{topic}'."

def recall_learnings(topic: str = "all") -> str:
    """
    Retrieves past learnings, skills, and observations from long-term memory.
    Provide a specific topic to filter, or 'all' to get a summary of everything.
    """
    mem = _load_memory()
    if not mem["skills"]:
        return "No learnings recorded yet."

    if topic != "all":
        if topic in mem["skills"]:
            lessons = "\n".join([f"- {entry['lesson']} ({entry['timestamp']})" for entry in mem["skills"][topic]])
            return f"Learnings for '{topic}':\n{lessons}"
        else:
            return f"No specific learnings found for topic '{topic}'. Available topics: {', '.join(mem['skills'].keys())}"

    # Return a summary of all topics
    summary = "All recorded skills/topics:\n"
    for t, entries in mem["skills"].items():
        summary += f"- {t} ({len(entries)} lessons)\n"
    return summary

# Export these explicitly
__tools__ = [record_learning, recall_learnings]
