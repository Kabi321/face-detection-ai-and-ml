# utils/search_logs.py

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from PIL import Image, ImageTk
from datetime import datetime

DB_PATH = "db/visitors.db"

def open_search_window():
    def search_logs():
        face_id = entry_id.get().strip()
        event_type = combo_type.get()
        date = entry_date.get().strip()

        query = "SELECT face_id, event_type, timestamp, image_path FROM visitor_events WHERE 1=1"
        params = []

        if face_id:
            query += " AND face_id LIKE ?"
            params.append(f"%{face_id}%")
        if event_type != "All":
            query += " AND event_type = ?"
            params.append(event_type.lower())
        if date:
            try:
                datetime.strptime(date, "%Y-%m-%d")
                query += " AND DATE(timestamp) = ?"
                params.append(date)
            except ValueError:
                messagebox.showerror("Invalid Date", "Date must be in YYYY-MM-DD format")
                return

        results.delete(*results.get_children())

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            results.insert("", "end", values=row)

    window = tk.Toplevel()
    window.title("🔎 Search Visitor Logs")
    window.geometry("880x500")
    window.configure(bg="#f9f9f9")

    # Filters Frame
    filter_frame = tk.Frame(window, bg="#f9f9f9")
    filter_frame.pack(pady=20)

    tk.Label(filter_frame, text="Face ID:", bg="#f9f9f9").grid(row=0, column=0, padx=10)
    entry_id = tk.Entry(filter_frame, width=20)
    entry_id.grid(row=0, column=1)

    tk.Label(filter_frame, text="Event Type:", bg="#f9f9f9").grid(row=0, column=2, padx=10)
    combo_type = ttk.Combobox(filter_frame, values=["All", "entry", "exit"], state="readonly", width=10)
    combo_type.set("All")
    combo_type.grid(row=0, column=3)

    tk.Label(filter_frame, text="Date (YYYY-MM-DD):", bg="#f9f9f9").grid(row=0, column=4, padx=10)
    entry_date = tk.Entry(filter_frame, width=15)
    entry_date.grid(row=0, column=5)

    tk.Button(filter_frame, text="🔍 Search", command=search_logs, bg="#3498db", fg="white",
              font=("Arial", 10, "bold"), padx=10, pady=3).grid(row=0, column=6, padx=20)

    # Results Table
    columns = ("Face ID", "Type", "Timestamp", "Image Path")
    results = ttk.Treeview(window, columns=columns, show="headings", height=15)
    for col in columns:
        results.heading(col, text=col)
        results.column(col, width=200 if col == "Image Path" else 120)

    results.pack(fill=tk.BOTH, padx=20, pady=10)

    def on_double_click(event):
        item = results.selection()
        if item:
            _, _, _, image_path = results.item(item[0], "values")
            if os.path.exists(image_path):
                top = tk.Toplevel(window)
                top.title("🖼️ Log Image Preview")

                img = Image.open(image_path)
                img.thumbnail((300, 300))
                photo = ImageTk.PhotoImage(img)

                img_label = tk.Label(top, image=photo)
                img_label.image = photo
                img_label.pack(padx=10, pady=10)
            else:
                messagebox.showerror("Not Found", "Image file does not exist.")

    results.bind("<Double-1>", on_double_click)
