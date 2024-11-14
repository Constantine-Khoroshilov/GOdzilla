from ultralytics import YOLO
import numpy as np

def detect_hands(image: np.ndarray):
    model = YOLO(r"..\best.pt") # путь до модели
    results = model.predict(source=image, save=False)

    arary_of_type = []
    i = 0
    for result in results:
        arary_of_type.append(len(results[i].boxes.conf.cpu().numpy()) != 0)
        i += 1

    return arary_of_type[0]

