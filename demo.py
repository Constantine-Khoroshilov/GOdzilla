from stones_detector import StonesDetector
from hands_detector import detect_hands
import cv2


start_point = None
end_point = None
drawing = False

def draw_rectangle(event, x, y, a, b):
    global start_point, end_point, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)
        end_point = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_point = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)


cap = cv2.VideoCapture('test\\debug.mp4')

width = int(cap.get(3))
height = int(cap.get(4))

cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Video', width // 2, height // 2)
cv2.setMouseCallback('Video', draw_rectangle)


ret, frame = cap.read()
if not ret:
    print("Ошибка: Не удалось прочитать кадр.")
    exit()

while True:
    temp_frame = frame.copy()

    if drawing:
        cv2.rectangle(temp_frame, start_point, end_point, (0, 255, 0), 2)

    cv2.imshow('Video', temp_frame)

    if cv2.waitKey(30) & 0xFF == ord('c'):
        break


if start_point and end_point:
    print("Координаты верхней левой точки:", start_point)
    print("Координаты правой нижней точки:", end_point)

detector = StonesDetector(start_point[0], start_point[1], end_point[0], end_point[1], size=13)

is_show_matrix = True
while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow('Video', frame)

    is_hand = detect_hands(frame)
    if is_hand:
        is_show_matrix = True

    if not is_hand and is_show_matrix:
        print()
        matrix = detector.get_stones_matrix(frame)
        for i in matrix:
            print(*i, sep=' ')

        is_show_matrix = False

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
