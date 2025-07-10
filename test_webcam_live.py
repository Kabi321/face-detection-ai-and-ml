import cv2
import time
import signal
import sys
from detection.face_detector import FaceDetector
from recognition.face_recognizer import FaceRecognizer
from tracking.tracker import CentroidTracker
from logger import save_face_event
from db.database import init_db, count_daily_unique_visitors

# Global variable to control the loop
running = True

def signal_handler(sig, frame):
    global running
    print("\n🛑 Received stop signal. Shutting down...")
    running = False

# Initialize DB and components
init_db()
face_detector = FaceDetector(conf_threshold=0.5)
face_recognizer = FaceRecognizer()
tracker = CentroidTracker()

# Tracking structures
active_faces = {}         # {face_id: last_seen_frame}
face_crops = {}           # {face_id: last_seen_crop}
frame_count = 0
detection_skip = 5

# Set up signal handler for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# 📷 Use laptop webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Could not access the webcam.")
    exit()

print("📷 Webcam started. Press 'q' to quit or Ctrl+C to stop.\n")

while running:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame.")
        break

    frame_count += 1
    if frame_count % detection_skip != 0:
        continue

    detections = face_detector.detect_faces(frame)
    print(f"🧠 Detections found: {len(detections)}")

    rects, crops = [], []

    for box in detections:
        x1, y1, x2, y2 = [int(c) for c in box['bbox']]
        if 0 <= x1 < x2 <= frame.shape[1] and 0 <= y1 < y2 <= frame.shape[0]:
            w, h = x2 - x1, y2 - y1
            rects.append((x1, y1, w, h))
            crops.append(frame[y1:y2, x1:x2])
        else:
            print(f"⚠️ Skipping invalid box: {box}")

    tracked_objects = tracker.update(rects)
    seen_this_frame = set()

    for (tracker_id, (x, y, w, h)) in tracked_objects.items():
        x1, y1, x2, y2 = x, y, x + w, y + h

        matched_crop = None
        for (rx, ry, rw, rh), crop in zip(rects, crops):
            if abs(rx - x) < 20 and abs(ry - y) < 20:
                matched_crop = crop
                break

        if matched_crop is not None:
            face_id = face_recognizer.recognize_face(matched_crop)

            if face_id not in active_faces:
                save_face_event(matched_crop, face_id, "entry")
                print(f"📸 ENTRY logged for {face_id}")

            active_faces[face_id] = frame_count
            face_crops[face_id] = matched_crop
            seen_this_frame.add(face_id)

            label = f"ID: {face_id} | TID: {tracker_id}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    disappeared = []
    for face_id, last_seen in active_faces.items():
        if face_id not in seen_this_frame and frame_count - last_seen > 30:
            last_crop = face_crops.get(face_id)
            if last_crop is not None:
                save_face_event(last_crop, face_id, "exit")
                print(f"📸 EXIT logged for {face_id}")
            disappeared.append(face_id)

    for face_id in disappeared:
        active_faces.pop(face_id, None)
        face_crops.pop(face_id, None)

    # 💻 Show resized window
    resized_frame = cv2.resize(frame, (960, 720))
    cv2.imshow("📷 Live Face Tracking (Press 'q' to quit)", resized_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("🛑 Stopped by user.")
        break
    
    # Check if we should stop
    if not running:
        print("🛑 Stopping webcam...")
        break

cap.release()
cv2.destroyAllWindows()

# 📊 Show visitor count
print("\n📊 Daily Unique Visitors:")
daily_counts = count_daily_unique_visitors()
for visit_date, count in daily_counts:
    print(f"📅 {visit_date}: {count} unique visitors")
