import sqlite3
import os
from datetime import datetime

DB_PATH = "db/visitors.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visitor_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            face_id TEXT,
            event_type TEXT,
            timestamp TEXT,
            image_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_event(face_id, event_type, image_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO visitor_events (face_id, event_type, timestamp, image_path)
        VALUES (?, ?, ?, ?)
    ''', (face_id, event_type, timestamp, image_path))
    conn.commit()
    conn.close()

def count_daily_unique_visitors():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DATE(timestamp) as visit_date, COUNT(DISTINCT face_id) as unique_visitors
        FROM visitor_events
        WHERE event_type = 'entry'
        GROUP BY visit_date
        ORDER BY visit_date DESC
    ''')
    results = cursor.fetchall()
    conn.close()
    return results
