import os
import pickle
import uuid
import cv2
import numpy as np
from insightface.app import FaceAnalysis

class FaceRecognizer:
    def __init__(self,
                 embeddings_path="embeddings/face_embeddings.pkl",
                 registered_dir="registered_faces"):
        self.embeddings_path = embeddings_path
        self.registered_dir = registered_dir
        os.makedirs(registered_dir, exist_ok=True)
        os.makedirs(os.path.dirname(embeddings_path), exist_ok=True)

        self.face_db = {}  # {face_id or name: embedding}
        self._load_embeddings()

        self.app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0)

    def _load_embeddings(self):
        if os.path.exists(self.embeddings_path):
            with open(self.embeddings_path, "rb") as f:
                self.face_db = pickle.load(f)
            print(f"📦 Loaded {len(self.face_db)} embeddings.")
        else:
            print("📁 No embeddings found. Starting fresh.")

    def _save_embeddings(self):
        with open(self.embeddings_path, "wb") as f:
            pickle.dump(self.face_db, f)

    def recognize_face(self, face_crop):
        face_crop_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
        faces = self.app.get(face_crop_rgb)

        if len(faces) == 0:
            return None  # No face found

        embedding = faces[0].embedding

        # Find best match
        best_id, best_dist = None, float('inf')
        for face_id, stored_emb in self.face_db.items():
            dist = np.linalg.norm(stored_emb - embedding)
            if dist < best_dist:
                best_dist = dist
                best_id = face_id

        if best_dist < 0.6:
            return best_id
        else:
            # New face: ask for name
            from utils.name_prompt import prompt_for_name  # 🆕 Dynamically import to avoid early GUI
            name = prompt_for_name("Unnamed")
            name = name.strip().replace(" ", "_")

            # Ensure uniqueness
            if name in self.face_db:
                name = f"{name}_{str(uuid.uuid4())[:4]}"

            self.face_db[name] = embedding
            self._save_embeddings()

            # Save cropped image
            filename = os.path.join(self.registered_dir, f"{name}.jpg")
            cv2.imwrite(filename, face_crop)

            print(f"🆕 Registered new face: {name}")
            return name
