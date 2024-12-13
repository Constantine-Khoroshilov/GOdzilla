from itertools import count
from process_video import process_video
from model import Video, Processing
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


video = Video('ID')
video.path = 'tests\\debug3.mkv'
video.segment = Video.Segment(start=0, stop=38)
video.processing.status = Processing.Status.RUNNING
video.processing.sgf_path = 'debug.sgf'

cap = cv2.VideoCapture(video.path)

width = int(cap.get(3))
height = int(cap.get(4))

cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Video', width // 2, height // 2)
cv2.setMouseCallback('Video', draw_rectangle)

ret, frame = cap.read()
if not ret:
    print("Ошибка: Не удалось прочитать кадр.")
    exit()

counter = 0
while True:
    if counter < 15:
        ret, frame = cap.read()
        counter += 1
        continue

    temp_frame = frame.copy()

    if drawing:
        cv2.rectangle(temp_frame, start_point, end_point, (0, 255, 0), 2)

    cv2.imshow('Video', temp_frame)

    if cv2.waitKey(30) & 0xFF == ord('c'):
        break

cap.release()
cv2.destroyAllWindows()

if start_point and end_point:
    print("Координаты верхней левой точки:", start_point)
    print("Координаты правой нижней точки:", end_point)

    
video.board_area = Video.BoardArea(x1=start_point[0], y1=start_point[1], x2=end_point[0], y2=end_point[1])
process_video(video, video.processing)
