# utils/export_csv.py

import sqlite3
import csv
import os

DB_PATH = "db/visitors.db"
EXPORT_PATH = "logs/visitor_log.csv"

def export_csv():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM visitor_events")
    rows = cursor.fetchall()
    conn.close()

    os.makedirs("logs", exist_ok=True)
    with open(EXPORT_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Face ID", "Event Type", "Timestamp", "Image Path"])
        writer.writerows(rows)
