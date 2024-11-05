from ultralytics import YOLO

def HandFinder(numpydata):
    model = YOLO(r"..\best.pt")# путь до модели
    results = model.predict(source=numpydata,save=False)
    AraryOfType =[]
    i=0
    for result in results:
        AraryOfType.append(len(results[i].boxes.conf.cpu().numpy())!=0)
        i+=1
    return AraryOfType[0]

