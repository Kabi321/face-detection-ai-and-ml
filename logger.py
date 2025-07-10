# logger.py

import os
import cv2
from datetime import datetime
from db.database import log_event

def save_face_event(face_crop, face_id, event_type):
    if face_crop is None or face_id is None:
        print(f"⚠️ Skipping log: face_crop or face_id is None")
        return

    # Format timestamp and path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = "logs/entries" if event_type == "entry" else "logs/exits"
    os.makedirs(folder, exist_ok=True)

    # Sanitize filename
    safe_face_id = str(face_id).replace(" ", "_")
    filename = f"{safe_face_id}_{timestamp}.jpg"
    path = os.path.join(folder, filename)

    # Save image
    try:
        success = cv2.imwrite(path, face_crop)
        if success:
            log_event(face_id, event_type, path)
            print(f"📸 {event_type.upper()} logged for {face_id} at {timestamp}")
        else:
            print(f"❌ Failed to save image for {face_id}")
    except Exception as e:
        print(f"❌ Exception saving event for {face_id}: {e}")
