# backend/app/chat_store.py
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from uuid import uuid4

STORAGE = os.path.join(os.path.dirname(__file__), "chats_store.json")

def _load_all():
    if not os.path.exists(STORAGE):
        return []
    with open(STORAGE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []

def _save_all(data):
    with open(STORAGE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def list_chats() -> List[Dict]:
    return sorted(_load_all(), key=lambda x: x.get("updated_at", ""), reverse=True)

def create_chat(title: str="New chat") -> Dict:
    chats = _load_all()
    chat = {
        "id": str(uuid4()),
        "title": title,
        "messages": [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    chats.append(chat)
    _save_all(chats)
    return chat

def get_chat(chat_id: str) -> Optional[Dict]:
    chats = _load_all()
    for c in chats:
        if c["id"] == chat_id:
            return c
    return None

def update_chat(chat_id: str, messages: List[Dict], title: Optional[str]=None) -> Optional[Dict]:
    chats = _load_all()
    for i,c in enumerate(chats):
        if c["id"] == chat_id:
            c["messages"] = messages
            if title:
                c["title"] = title
            c["updated_at"] = datetime.utcnow().isoformat()
            chats[i] = c
            _save_all(chats)
            return c
    return None

def delete_chat(chat_id: str) -> bool:
    chats = _load_all()
    new = [c for c in chats if c["id"] != chat_id]
    if len(new) == len(chats):
        return False
    _save_all(new)
    return True

def rename_chat(chat_id: str, title: str) -> Optional[Dict]:
    chats = _load_all()
    for i,c in enumerate(chats):
        if c["id"] == chat_id:
            c["title"] = title
            c["updated_at"] = datetime.utcnow().isoformat()
            chats[i] = c
            _save_all(chats)
            return c
    return None
