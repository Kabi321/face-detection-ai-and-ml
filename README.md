
# 🤖 Intelligent Face Tracker (by Team IntelligentVision)

Welcome to the **Intelligent Face Tracker**, a smart real-time system for face detection, recognition, tracking, and visitor analytics. Designed for Hackathons and smart surveillance, this tool automatically detects faces, recognizes known visitors, registers new ones, and logs entry/exit events with time and images.

---

## 🎯 Features

✅ Real-time Face Detection using YOLOv8  
✅ Face Recognition with Auto Registration (ArcFace / InsightFace)  
✅ Entry/Exit Event Logging with Timestamps  
✅ Daily Unique Visitor Counting  
✅ GUI Dashboard (Start/Stop, Export Logs, Search Logs)  
✅ Auto Name Prompt for New Faces  
✅ Export Visitor Logs to CSV  
✅ Multithreading Support for Responsive GUI  
✅ SQLite3-backed Event Logging

---

## 📂 Project Structure

```bash
IntelligentFaceTracker/
├── detection/
│   └── face_detector.py
├── recognition/
│   └── face_recognizer.py
├── tracking/
│   └── tracker.py
├── gui/
│   └── dashboard.py
├── utils/
│   ├── name_prompt.py
│   ├── search_logs.py
│   └── export_csv.py
├── db/
│   └── database.py
├── logs/
│   ├── entries/
│   ├── exits/
│   └── visitor_log.csv
├── registered_faces/
├── embeddings/
│   └── face_embeddings.pkl
├── videos/
│   └── <your_input_videos>.mp4
├── test_multiple_videos.py
├── README.md
└── requirements.txt
````

---

## 🚀 How to Run

### 1️⃣ Setup Environment

Install dependencies using:

```bash
pip install -r requirements.txt
```

### 2️⃣ Add Videos

Place `.mp4` video files inside the `videos/` directory.

### 3️⃣ Launch Dashboard (GUI)

```bash
python gui/dashboard.py
```

Use the GUI to:

* ▶ Start Tracking
* ⛔ Stop Tracking
* 📁 Export Visitor Logs
* 🔍 Search Logs

---

## 🔍 Example Outputs

* Logs saved in `logs/entries/` and `logs/exits/` with timestamped images.
* SQLite DB saved in `db/visitors.db`.
* Exported logs as `logs/visitor_log.csv`.

---

## 👨‍💻 Built With

* [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
* [InsightFace (ArcFace)](https://github.com/deepinsight/insightface)
* [Tkinter](https://docs.python.org/3/library/tkinter.html) – for GUI
* [OpenCV](https://opencv.org/)
* [SQLite3](https://sqlite.org)

---

## 🧠 Team IntelligentVision

A dedicated team for crafting smart and intuitive face-tracking solutions during the 2025 Hackathon!

> "Detect. Recognize. Track. Log. Visualize." 🚀

---

## 📝 License

This project is built for educational and Hackathon purposes only.

````

---

### ✅ `requirements.txt`

```text
opencv-python
ultralytics
insightface
numpy
pillow
tk
````




python -m gui.dashboard
