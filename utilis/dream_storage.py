# utils/dream_storage.py

import sqlite3
import json
import os

DB_PATH = "dreams.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS dreams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            emotions TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def store_dream(text, emotions):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO dreams (text, emotions) VALUES (?, ?)", (text, json.dumps(emotions)))
    conn.commit()
    conn.close()

def get_dreams():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT text, emotions, timestamp FROM dreams ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    dreams = []
    for text, emotions_json, timestamp in rows:
        try:
            emotions = json.loads(emotions_json)
        except:
            emotions = {}
        dreams.append({
            "text": text,
            "emotions": emotions,
            "timestamp": timestamp
        })
    return dreams
