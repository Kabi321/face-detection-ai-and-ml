# utils/name_prompt.py

import tkinter as tk
from tkinter import simpledialog

def prompt_for_name(default="Unnamed"):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    name = simpledialog.askstring("👤 New Face Detected", "Enter name for new face:", initialvalue=default)
    root.destroy()
    return name if name else default