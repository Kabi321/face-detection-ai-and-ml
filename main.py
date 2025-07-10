import cv2
import os
from detection.face_detector import FaceDetector
from recognition.face_recognizer import FaceRecognizer
from tracking.tracker import Tracker
from logging.logger import EventLogger
from utils.helper_functions import crop_face, get_timestamp
from db.database import Database
import json

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

video_path = "videos/sample_video.mp4"
cap = cv2.VideoCapture(video_path)

# Initialize modules
face_detector = FaceDetector(conf_threshold=config["confidence_threshold"])
face_recognizer = FaceRecognizer()
tracker = Tracker()
logger = EventLogger()
db = Database()

frame_count = 0
skip_frames = config["skip_frames"]

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    detections = []

    if frame_count % skip_frames == 0:
        # Step 1: Detect faces
        detections = face_detector.detect_faces(frame)

        # Step 2: Recognize faces (generate embeddings + match DB)
        for det in detections:
            face_img = crop_face(frame, det['bbox'])
            face_id, is_new = face_recognizer.identify_or_register(face_img)

            det["face_id"] = face_id
            det["is_new"] = is_new

            if is_new:
                db.register_face(face_id, get_timestamp(), face_img)
                logger.log_event("entry", face_id, face_img)

    # Step 3: Track faces
    tracked_faces = tracker.update(detections, frame)

    # Step 4: Check for exits
    exited_ids = tracker.get_exited_faces()
    for face_id in exited_ids:
        logger.log_event("exit", face_id)

    # Optional: Show annotated frame
    # cv2.imshow("Face Tracker", frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

cap.release()
cv2.destroyAllWindows()
