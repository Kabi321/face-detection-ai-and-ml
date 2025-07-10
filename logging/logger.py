import logging
import os
import cv2
from datetime import datetime

logger = logging.getLogger("FaceLogger")
logger.setLevel(logging.INFO)

handler = logging.FileHandler("face_log.log")
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def save_face_image(face_img, name, face_id):
    folder = "detected_faces"
    os.makedirs(folder, exist_ok=True)

    filename = f"{name}_{face_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    path = os.path.join(folder, filename)

    cv2.imwrite(path, face_img)
