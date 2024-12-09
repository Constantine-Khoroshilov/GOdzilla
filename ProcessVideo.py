import cv2
import numpy as np
from stones_detector import StonesDetector
from hands_detector import detect_hands
from сreate_sgf import create_sgf

def process_video(video, processing, sgf_path):
    input_video_path = video.path
    start_time = video.segment.start
    end_time =  video.segment.stop
    whose_move = {
        1:"b",
        2:"w"
    }
    cap = cv2.VideoCapture(input_video_path)
    x1,y1,x2,y2 = video.BoardArea.x1,video.BoardArea.y1,video.BoardArea.x2,video.BoardArea.y2
    bild_matrix = StonesDetector(x1,y1,x2,y2)
    matrix =  np.zeros((19, 19), dtype=int)
    move_list =[]
    if not cap.isOpened():
        raise Exception('не удалось открыть видео')
    else:
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        # Вычисляем общее количество кадров для обрезки
        start_frame = start_time * fps
        end_frame = end_time * fps

        current_frame =0
        while True:
            processing.break_processing(cap.release)
            ret, frame = cap.read()
            if not ret:
                break

            if start_frame <= current_frame < end_frame:
                if not detect_hands(frame):
                    new_matrix = bild_matrix.get_stones_matrix(frame)
                    difference = new_matrix - matrix
                    coordinates = np.argwhere(difference > 0)
                    x, y  = coordinates[0, 0], coordinates[0, 1]
                    temp = (whose_move[new_matrix[x, y]], (x + 1, abs(y - 18)))
                    move_list.append(temp)
                    matrix = new_matrix.copy()

            current_frame +=1
            if current_frame > end_frame:  # Нажмите 'Esc' для выхода
                break
        cap.release()
    create_sgf(sgf_path,move_list)
