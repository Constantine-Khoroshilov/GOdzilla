from ultralytics import YOLO
import numpy as np
model = YOLO(r"models_parameters/hands_detector/best.pt",verbose=False) # путь до модели
def detect_hands(image: np.ndarray):
    results = model.predict(source=image, save=False, verbose=False)
    return len(results[0].boxes.conf.cpu().numpy()) != 0