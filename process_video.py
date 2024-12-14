from stones_detector import StonesDetector
from hands_detector import detect_hands
from сreate_sgf import create_sgf
import numpy as np
import cv2


whose_move = {
    1:"b",
    2:"w"
}


def cut_frame(frame, board_area):
    h, w = frame.shape[:2]
    x1, y1, x2, y2 = board_area

    dy, dx = int(0.1 * h), int(0.1 * w)

    # Проверка границ
    y1 = max(0, y1 - dy)
    y2 = min(h, y2 + dy)
    x1 = max(0, x1 - dx)
    x2 = min(w, x2 + dx)

    new_frame = frame[y1:y2, x1:x2]
    return new_frame


def process_video(video, processing, size=9):
    cap = cv2.VideoCapture(video.path)
    if not cap.isOpened():
        raise Exception('не удалось открыть видео')

    start_time = video.segment.start
    end_time = video.segment.stop

    board_area = video.board_area.x1, video.board_area.y1, video.board_area.x2, video.board_area.y2
    detector = StonesDetector(*board_area, size=size)
    detector.debug = True

    matrix = np.zeros((size, size), dtype=int)
    moves_list = []

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    # Вычисляем общее количество кадров для обрезки
    start_frame = start_time * fps
    end_frame = end_time * fps

    time_interval = 0.5 # 500 мс
    frames_to_skip = int(fps * time_interval)

    current_frame = 0
    while True:
        processing.break_processing(cap.release)
        ret, frame = cap.read()
        if not ret:
            break

        if current_frame % frames_to_skip == 0 and start_frame <= current_frame < end_frame:
            if not detect_hands(cut_frame(frame, board_area)):
                new_matrix = detector.get_stones_matrix(frame)
                difference = new_matrix - matrix

                coordinates = np.argwhere(difference > 0)
                if coordinates.size > 0:
                    y, x = coordinates[0, 0], coordinates[0, 1]
                    move = (whose_move[int(new_matrix[y, x])],(int(x + 1), int(abs(y - size)))) # abs(y - 18)))
                    moves_list.append(move)
                    matrix = new_matrix.copy()

        current_frame +=1

    cap.release()
    create_sgf(processing.sgf_path, moves_list)
