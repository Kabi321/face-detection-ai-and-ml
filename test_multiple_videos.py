import os
import cv2
import time
from detection.face_detector import FaceDetector
from recognition.face_recognizer import FaceRecognizer
from tracking.tracker import CentroidTracker
from logger import save_face_event
from db.database import init_db, count_daily_unique_visitors  # ✅ Import visitor count

# === Initialize DB and components ===
init_db()
face_detector = FaceDetector(conf_threshold=0.5)
face_recognizer = FaceRecognizer()
tracker = CentroidTracker()

# === Tracking data ===
active_faces = {}         # {face_id: last_seen_frame}
face_crops = {}           # {face_id: last_seen_crop}
frame_count = 0
detection_skip = 5

# === Load video files ===
video_folder = "videos"
video_files = sorted([f for f in os.listdir(video_folder) if f.endswith(".mp4")])

print("📁 Found videos:", video_files)

# === Process each video ===
for video_file in video_files:
    video_path = os.path.join(video_folder, video_file)
    print(f"\n▶️ Starting video: {video_file}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Could not open {video_file}")
        continue
    print(f"✅ Processing {video_file}...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"⏭️ Finished {video_file}")
            break

        frame_count += 1
        if frame_count % detection_skip != 0:
            continue

        detections = face_detector.detect_faces(frame)
        print(f"🧠 Detections found: {len(detections)}")

        rects = []
        crops = []

        for box in detections:
            x1, y1, x2, y2 = [int(c) for c in box['bbox']]
            if 0 <= x1 < x2 <= frame.shape[1] and 0 <= y1 < y2 <= frame.shape[0]:
                w = x2 - x1
                h = y2 - y1
                rects.append((x1, y1, w, h))
                crops.append(frame[y1:y2, x1:x2])
            else:
                print(f"⚠️ Skipping invalid box: {box}")

        # === Update tracker ===
        tracked_objects = tracker.update(rects)
        seen_this_frame = set()

        for (tracker_id, (x, y, w, h)) in tracked_objects.items():
            x1, y1, x2, y2 = x, y, x + w, y + h

            # Find matched crop for this tracker box
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

                # === Draw bounding box and label ===
                label = f"ID: {face_id} | TID: {tracker_id}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # === Handle disappearances ===
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

        # === Resize frame for display (1280x720) ===
        frame_resized = cv2.resize(frame, (1280, 720))
        cv2.imshow("Face Detection + Recognition + Tracking", frame_resized)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("⏩ Skipped by user")
            break

    cap.release()

cv2.destroyAllWindows()
print("\n🏁 All videos processed.")

# === Show unique visitor summary ===
print("\n📊 Daily Unique Visitors:")
daily_counts = count_daily_unique_visitors()
for visit_date, count in daily_counts:
    print(f"📅 {visit_date}: {count} unique visitors")
