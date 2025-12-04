import os
import json
from typing import List

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "storage")
os.makedirs(STORAGE_DIR, exist_ok=True)

def _path(user_id: str) -> str:
    safe = "".join(c for c in user_id if c.isalnum() or c in ("-", "_"))
    return os.path.join(STORAGE_DIR, f"{safe}.json")

def load(user_id: str) -> List[dict]:
    p = _path(user_id)
    if not os.path.exists(p):
        return []
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save(user_id: str, messages: List[dict]) -> None:
    p = _path(user_id)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def clear(user_id: str) -> None:
    p = _path(user_id)
    if os.path.exists(p):
        os.remove(p)
