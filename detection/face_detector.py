from ultralytics import YOLO

class FaceDetector:
    def __init__(self, model_path="models/yolov8n-face-lindevs.pt", conf_threshold=0.5):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold

    def detect_faces(self, frame):
        results = self.model.predict(frame, conf=self.conf_threshold, verbose=False)
        detections = []

        if results and len(results[0].boxes) > 0:
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "confidence": conf
                })

        return detections
