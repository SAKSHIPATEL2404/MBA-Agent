
import sqlite3, os, json

class Memory:
    def __init__(self, path="./app/models/memory.db"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self._init()

    def _init(self):
        cur = self.conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS conversations (
            user_id TEXT,
            role TEXT,
            text TEXT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
        self.conn.commit()

    def add(self, user_id, role, text):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO conversations (user_id, role, text) VALUES (?, ?, ?)", (user_id, role, text))
        self.conn.commit()

    def get(self, user_id, limit=50):
        cur = self.conn.cursor()
        cur.execute("SELECT role, text, ts FROM conversations WHERE user_id=? ORDER BY ts DESC LIMIT ?", (user_id, limit))
        rows = cur.fetchall()
        rows = rows[::-1]
        return [{"role": r[0], "text": r[1], "ts": r[2]} for r in rows]
