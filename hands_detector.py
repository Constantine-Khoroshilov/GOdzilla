from ultralytics import YOLO
import numpy as np
def detect_hands(image: np.ndarray):
    model = YOLO(r"C:\Users\kondr\godzilla\Branch\GOdzilla\models_parameters\hands_detector\best.pt") # путь до модели
    results = model.predict(source=image, save=True)
    return len(results[0].boxes.conf.cpu().numpy())!= 0



