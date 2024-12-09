import cv2
import numpy
from stones_detector import StonesDetector
from hands_detector import detect_hands


def select_roi(frame):
    # Выбор области интереса с помощью cv2.selectROI
    bbox = cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow("Frame")  # Закрытие окна после выбора

    return bbox  # Возвращаем координаты (x, y, w, h)


input_video_path = "../../Pricessing_video/debug.mp4"
output_video_path = "../../Pricessing_video/testVideo4.mp4"
start_time = 55
end_time =  1000  #5151
# Координаты обрезки (x1, y1) - верхний левый угол, (x2, y2) - нижний правый угол

cap = cv2.VideoCapture(input_video_path)
width = int(cap.get(3)) # cv2.CAP_PROP_FRAME_WIDTH
height = int(cap.get(4)) # cv2.CAP_PROP_FRAME_HEIGHT
if not cap.isOpened():
    print("Ошибка: не удалось открыть видео.")


else:
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    # Вычисляем общее количество кадров для обрезки
    start_frame = start_time * fps
    end_frame = end_time * fps

    current_frame =0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Ошибка: завершение видео или ошибка чтения!")
            break
        if current_frame == 0:
            x1,y1,x2,y2 = select_roi(frame)
            bild_matrix = StonesDetector(x1, y1, x2, y2)
        cropped_frame = frame[y1:y2, x1:x2]
        cv2.imshow("tt",cropped_frame)
        if start_frame <= current_frame < end_frame:
            matrix = bild_matrix.get_stones_matrix(cropped_frame)
            print(matrix)
        current_frame +=1
        if current_frame > end_frame:  # Нажмите 'Esc' для выхода
            break

    cap.release()
    cv2.destroyAllWindows()
    '''
    # Получаем параметры видео
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    # Вычисляем общее количество кадров для обрезки
    start_frame = start_time * fps
    end_frame = end_time * fps

    #fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Кодек для mp4
    #out = cv2.VideoWriter(output_video_path, fourcc, fps, (x2-x1, y2-y1))

    current_frame = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # Выход, если не удается прочитать кадр
        cropped_frame = frame[y1:y2, x1:x2]

        if start_frame <= current_frame < end_frame:
            image_rgb = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB)
            if not detect_hands(image_rgb):
                #out.write(cropped_frame)
                cv2.imshow('Video', frame)
                #new_move =  bild_matrix.get_stones_matrix(frame)
                #print(new_move)
                #move  = new_move
        elif current_frame > end_frame:
            break
        print(current_frame)

        current_frame += 1

    # Освобождаем ресурсы'''

