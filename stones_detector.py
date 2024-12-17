<<<<<<< HEAD
=======
from dbm import whichdb
>>>>>>> 287319b940b9f3131d960314f9283f9c46e532ea
import numpy as np
import cv2
import os


class StonesDetector:
    ''' Класс содержит методы, которые позволяют по
        изображению игровой доски ГО получить матрицу
        расположения камней.
        
        Элеметами матрицы выступают:
        1. 0 - камень отсутствует,
        2. 1 - камень черный,
        3. 2 - камень белый.
    '''
    def __init__(self, x1, y1, x2, y2, size=19):
        ''' На вход конструктору подаются:
                Область игровой доски на изображении:
                    x1, y1 - координаты левой верхней точки,
                    x2, y2 - координаты правой нижней точки,
            size - размерность матрицы (доски),
        '''
        self._size = size
<<<<<<< HEAD
        self._lt_x = x1
        self._lt_y = y1
        self._rb_x = x2
        self._rb_y = y2

        self._height = y2 - y1
        self._width = x2 - x1
        
        cascades_folder = os.path.join('models_parameters', 'stones_detector')
        self._black_cascade = cv2.CascadeClassifier(os.path.join(cascades_folder, 'black-cascade-grayscale.xml'))
        self._white_cascade = cv2.CascadeClassifier(os.path.join(cascades_folder, 'white-cascade-grayscale.xml'))
=======
        self._start = (y1, x1)
        self._end = (y2, x2)
        # длина и ширина игровой доски
        self._length = y2 - y1
        self._width = x2 - x1
        # шаг, с которым вычисляются координаты основных точек, на которых стоят камни
        self._step_y = (self._length - 1) / (self._size - 1)
        self._step_x = (self._width - 1) / (self._size - 1)
        # размеры половин сторон прямоугольной области, центром которой является основная точка
        self._ry = int(0.05 * self._step_y)
        self._rx = int(0.05 * self._step_x)

        self._black_cascade = cv2.CascadeClassifier(os.path.join('models_parameters', 'stones_detector', 'black-cascade-grayscale.xml'))
        self._white_cascade = cv2.CascadeClassifier(os.path.join('models_parameters', 'stones_detector', 'white-cascade-grayscale.xml'))
>>>>>>> 287319b940b9f3131d960314f9283f9c46e532ea
        
        self.debug = False


<<<<<<< HEAD
    def _detect_stones(self, src: np.ndarray, cascade: cv2.CascadeClassifier):
        min_size = (self._width // self._size, self._height // self._size)
        rects = cascade.detectMultiScale(
            src, 
            scaleFactor=1.1, 
            minNeighbors=3, 
            minSize=min_size, 
            flags=cv2.CASCADE_SCALE_IMAGE)
=======
    def _process_image(self, src: np.ndarray) -> np.ndarray:
        gray_img = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        # среднее значение
        mean_brightness = np.mean(gray_img)
        # стандартное отклонение — мера разброса значений относительно среднего
        std_brightness = np.std(gray_img) 

        # пороговые значения для выделения черных и белых камней
        tolerance = 0
        black_thresh = mean_brightness - (std_brightness * (1 + tolerance))
        white_thresh = mean_brightness + (std_brightness * (1 + tolerance))
            
        # итоговый цвет пикселей, текущий цвет к-ых превосходит порог
        maxval = 255

        _, black_stones_bin = cv2.threshold(gray_img, black_thresh, maxval, cv2.THRESH_BINARY)
        _, white_stones_bin = cv2.threshold(gray_img, white_thresh, maxval, cv2.THRESH_BINARY)

        black_stones_img = cv2.cvtColor(black_stones_bin, cv2.COLOR_GRAY2BGR)
        white_stones_img = cv2.cvtColor(white_stones_bin, cv2.COLOR_GRAY2BGR)

        black = np.array([0, 0, 0], dtype=int)
        white = np.array([255, 255, 255], dtype=int)
        blue = np.array([255, 0, 0], dtype=int)

        black_stones = np.all(black_stones_img == black, axis=-1)
        white_stones = np.all(white_stones_img == white, axis=-1)

        stones_img = np.full(src.shape, blue, dtype=np.uint8)
        stones_img[black_stones] = black
        stones_img[white_stones] = white

        return stones_img


    def _detect(self, src: np.ndarray, cascade):
        gray_img = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        min_size = (self._width // self._size, self._length // self._size)

        rects = cascade.detectMultiScale(
            gray_img, scaleFactor=1.1, minNeighbors=3, minSize=min_size, flags=cv2.CASCADE_SCALE_IMAGE)
>>>>>>> 287319b940b9f3131d960314f9283f9c46e532ea

        return rects


<<<<<<< HEAD
    def _is_inside_board(self, x, y, src_w, src_h):
        offset = 10
        X1 = self._lt_x - offset
        Y1 = self._lt_y - offset
        X2 = self._rb_x + offset
        Y2 = self._rb_y + offset

        X1 = max(0, X1)
        Y1 = max(0, Y1)
        X2 = min(src_w, X2)
        Y2 = min(src_h, Y2)

        return X1 < x < X2 and Y1 < y < Y2


    def _rect_to_point(self, rect):
        x, y, h, w = rect
        return x + w // 2, y + h // 2 


    def _get_pos_in_matrix(self, x, y):
        X = self._lt_x
        Y = self._lt_y
        w = self._width
        h = self._height

        row = int(round((y - Y) / h * (self._size - 1)))
        col = int(round((x - X) / w * (self._size - 1)))
        
        return row, col
=======
    def _is_point_inside(self, rects, px, py):
        for x, y, h, w in rects:
            if x < px < x + w and y < py < y + h:
                return True
        return False
>>>>>>> 287319b940b9f3131d960314f9283f9c46e532ea


    def get_stones_matrix(self, src: np.ndarray) -> np.ndarray:
        ''' Метод принимает на вход:
                src - открытое исходное изображение игровой доски ГО,                
            и возвращает матрицу расположения 
            камней на изображении.
        '''
<<<<<<< HEAD
        h, w = src.shape[:2]
        gray_img = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

        black_stones = self._detect_stones(gray_img, self._black_cascade)
        white_stones = self._detect_stones(gray_img, self._white_cascade)

        matrix = np.zeros((self._size, self._size), dtype=int)
        
        if self.debug:
            debug_image = src.copy()

        for stone in black_stones:
            cx, cy = self._rect_to_point(stone)

            if self.debug:
                cv2.rectangle(debug_image, (cx, cy), (cx, cy), (0, 255, 0), 10)

            if self._is_inside_board(cx, cy, w, h):
                j, i = self._get_pos_in_matrix(cx, cy)
                matrix[j][i] = 1

        for stone in white_stones:
            cx, cy = self._rect_to_point(stone)

            if self.debug:
                cv2.rectangle(debug_image, (cx, cy), (cx, cy), (0, 255, 0), 10)

            if self._is_inside_board(cx, cy, w, h):
                j, i = self._get_pos_in_matrix(cx, cy)
                matrix[j][i] = 2

        if self.debug:
            self._view_image(debug_image)
=======
        blurred_image = cv2.GaussianBlur(src, (51, 51), 0)
        precessed_image = self._process_image(blurred_image)

        black_stones = self._detect(src, self._black_cascade)
        white_stones = self._detect(src, self._white_cascade)

        if self.debug:
            self._view_image(precessed_image)

        matrix = np.zeros((self._size, self._size), dtype=int)

        for i in range(self._size):
            for j in range(self._size):
                # координаты основной точки, на которой расположен камень 
                x = self._start[0] + int(i * self._step_x) 
                y = self._start[1] + int(j * self._step_y)

                # координаты прямоугольной области
                y1 = y - self._ry if (y - self._ry) > self._start[0] else y
                y2 = y + self._ry if (y + self._ry) < self._end[0] else y
                x1 = x - self._rx if (x - self._rx) > self._start[1] else x
                x2 = x + self._rx if (x + self._rx) < self._end[1] else x
                
                colors = precessed_image[y1:y2,x1:x2]
                # средний цвет прямоугольной области
                color = cv2.mean(colors)[:3]

                if self._is_point_inside(black_stones, x, y):
                    matrix[j][i] = 1

                elif self._is_point_inside(white_stones, x, y):
                    matrix[j][i] = 2
                
                elif all(component < 100 for component in color):
                    matrix[j][i] = 1

                elif all(component > 200 for component in color):
                    matrix[j][i] = 2
                    
                if self.debug: 
                    yellow = (0, 255, 255)
                    cv2.rectangle(precessed_image, (x,y), (x,y), yellow, 5)
                    cv2.rectangle(precessed_image, (x1, y1), (x2, y2), yellow, 2)

                    for x, y, b, h in black_stones:
                        cv2.rectangle(precessed_image, (x, y), (x+b, y+h), yellow, 4)

                    for x, y, b, h in white_stones:
                        cv2.rectangle(precessed_image, (x, y), (x+b, y+h), yellow, 4)
      
        if self.debug:
            self._view_image(precessed_image)
>>>>>>> 287319b940b9f3131d960314f9283f9c46e532ea

        return matrix  


    def _view_image(self, image, window_name='Result of proccessing'):
        # Создание окна
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 800)
        cv2.imshow(window_name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()