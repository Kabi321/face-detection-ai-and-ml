import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
from utils.search_logs import open_search_window
from db.database import count_daily_unique_visitors
from datetime import datetime

class ModernDashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visitor Counting Dashboard")
        self.root.geometry("1080x640")
        self.root.configure(bg="#F0F2F5")
        self.root.resizable(False, False)

        # Header
        header = tk.Frame(root, bg="#3A3D46", height=70)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)

        title = tk.Label(header, text="📊 Visitor Counting System", font=("Segoe UI", 22, "bold"), bg="#3A3D46", fg="#FFFFFF")
        title.pack(side=tk.LEFT, padx=25)

        self.status_label = tk.Label(header, text="🟡 Idle", font=("Segoe UI", 14), bg="#3A3D46", fg="#FFC107")
        self.status_label.pack(side=tk.RIGHT, padx=25)

        # Content
        content = tk.Frame(root, bg="#F0F2F5")
        content.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        sidebar = tk.Frame(content, bg="#FFFFFF", width=260, bd=2, relief="groove")
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Dashboard Menu", font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg="#1E88E5").pack(pady=(20, 10))

        self.create_sidebar_button(sidebar, "▶ Play Video", "#1E88E5", lambda: self.start_tracking("test_multiple_videos.py"))
        self.create_sidebar_button(sidebar, "🎥 Live stream Webcam", "#43A047", lambda: self.start_tracking("test_webcam_live.py"))
        self.create_sidebar_button(sidebar, "⛔ Stop", "#E53935", self.stop_tracking, disabled=True)
        self.create_sidebar_button(sidebar, "📁 Export Logs", "#FB8C00", self.export_logs)
        self.create_sidebar_button(sidebar, "🔍 Search Logs", "#3949AB", open_search_window)

        # Main panel
        main_panel = tk.Frame(content, bg="#E3F2FD")
        main_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create stat cards with labels for updating
        self.visitors_today_card = self.create_stat_card(main_panel, "👤 Visitors Today", "0", "#1976D2")
        self.visitors_today_card.pack(pady=10, padx=30, fill=tk.X)
        
        self.total_visitors_card = self.create_stat_card(main_panel, "📊 Total Visitors", "0", "#00796B")
        self.total_visitors_card.pack(pady=10, padx=30, fill=tk.X)
        
        self.last_export_card = self.create_stat_card(main_panel, "📤 Last Export", "None", "#6A1B9A")
        self.last_export_card.pack(pady=10, padx=30, fill=tk.X)
        
        # Add refresh button
        refresh_btn = tk.Button(main_panel, text="🔄 Refresh Stats", font=("Segoe UI", 12, "bold"), 
                               bg="#FF9800", fg="white", command=self.refresh_stats)
        refresh_btn.pack(pady=10, padx=30, fill=tk.X)
        
        # Initial stats load
        self.refresh_stats()

        # Footer
        footer = tk.Label(root, text="Visitor Counting v1.0 © 2025 | Powered by AI-Tech", font=("Segoe UI", 10),
                          bg="#3A3D46", fg="#B0BEC5")
        footer.pack(side=tk.BOTTOM, fill=tk.X)

        self.process = None

    def create_sidebar_button(self, parent, text, color, command, disabled=False):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 12, "bold"), bg=color, fg="white",
                        relief=tk.RAISED, activebackground=color, padx=10, pady=8, command=command)
        btn.pack(pady=10, fill=tk.X, padx=20)
        if disabled:
            btn.config(state=tk.DISABLED)
            self.stop_button = btn
        elif "Video" in text:
            self.start_video_button = btn
        elif "Webcam" in text:
            self.start_webcam_button = btn

    def create_stat_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=color, height=80)
        card.pack_propagate(False)
        tk.Label(card, text=title, font=("Segoe UI", 12, "bold"), bg=color, fg="white").pack(anchor="w", padx=15, pady=(10, 0))
        tk.Label(card, text=value, font=("Segoe UI", 24, "bold"), bg=color, fg="#FFEB3B").pack(anchor="w", padx=15)
        return card

    def start_tracking(self, script_name):
        if self.process:
            return
        self.status_label.config(text="🟢 Running", fg="#4CAF50")
        self.start_video_button.config(state=tk.DISABLED)
        self.start_webcam_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        def run_script():
            self.process = subprocess.Popen(["/Users/kabineshsivasamy/face_tracker_venv/bin/python3", script_name])
            self.process.wait()
            self.status_label.config(text="🟡 Idle", fg="#FFC107")
            self.start_video_button.config(state=tk.NORMAL)
            self.start_webcam_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.process = None

        threading.Thread(target=run_script, daemon=True).start()

    def stop_tracking(self):
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except:
                self.process.kill()
            self.status_label.config(text="🔴 Stopped", fg="#E53935")
            self.start_video_button.config(state=tk.NORMAL)
            self.start_webcam_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.process = None

    def refresh_stats(self):
        try:
            # Get daily visitor counts
            daily_counts = count_daily_unique_visitors()
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Find today's count
            visitors_today = 0
            total_visitors = 0
            
            for date, count in daily_counts:
                total_visitors += count
                if date == today:
                    visitors_today = count
            
            # Update the stat cards
            self.update_stat_card(self.visitors_today_card, visitors_today)
            self.update_stat_card(self.total_visitors_card, total_visitors)
            
        except Exception as e:
            print(f"Error refreshing stats: {e}")
    
    def update_stat_card(self, card, value):
        # Find and update the value label in the card
        for widget in card.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget("font") == ("Segoe UI", 24, "bold"):
                widget.config(text=str(value))
                break

    def export_logs(self):
        try:
            from utils.export_csv import export_csv
            export_csv()
            messagebox.showinfo("✅ Exported", "CSV logs exported successfully!")
            # Refresh stats after export
            self.refresh_stats()
        except Exception as e:
            messagebox.showerror("❌ Error", f"Export failed:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernDashboardApp(root)
    root.mainloop()
