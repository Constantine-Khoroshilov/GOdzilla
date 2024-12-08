from dbm import whichdb
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
        
        self.decreasor = 0.2
        self.color_detection = False
        self.debug = False


    def _process_image(self, src: np.ndarray) -> np.ndarray:
        blurred_image = cv2.GaussianBlur(src, (51, 51), 0)
        gray_img = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2GRAY)

        # среднее значение
        # mean_brightness = np.mean(gray_img)
        median_brightness = np.median(gray_img)

        # стандартное отклонение — мера разброса значений относительно среднего
        # std_brightness = np.std(gray_img)

        # Вычисление отклонений от медианы
        # deviations = gray_img - median_brightness
        # Вычисление стандартного отклонения от медианы
        # std_brightness = np.sqrt(np.mean(deviations**2))
        
        # медианное абсолютное отклонение
        std_brightness = np.median(np.abs(gray_img - median_brightness))

        # пороговые значения для выделения черных и белых камней
        tolerance = 0
        black_thresh = median_brightness - (std_brightness * (1 + tolerance))
        white_thresh = median_brightness + (std_brightness * (1 + tolerance))
            
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
        min_size = (self._width // self._size, self._length // self._size)
        rects = cascade.detectMultiScale(
            src, scaleFactor=1.1, minNeighbors=3, minSize=min_size, flags=cv2.CASCADE_SCALE_IMAGE)

        return rects


    def _is_point_inside(self, rects, px, py):
        for x, y, h, w in rects:
            if x < px < x + w and y < py < y + h:
                return True
        return False


    def _decrease_rect(self, rect):
        return np.array([
            rect[0] + self.decreasor * self._step_x,
            rect[1] + self.decreasor * self._step_y,
            rect[2] - 2 * self.decreasor * self._step_x,
            rect[3] - 2 * self.decreasor * self._step_y
        ], dtype=int)


    def get_stones_matrix(self, src: np.ndarray) -> np.ndarray:
        ''' Метод принимает на вход:
                src - открытое исходное изображение игровой доски ГО,                
            и возвращает матрицу расположения 
            камней на изображении.
        '''
        if self.color_detection:            
            precessed_image = self._process_image(src)
        else:
            precessed_image = src.copy()
        
        gray_img = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        black_stones = self._detect(gray_img, self._black_cascade)
        white_stones = self._detect(gray_img, self._white_cascade)

        if len(black_stones) != 0:
            black_stones = np.apply_along_axis(self._decrease_rect, axis=1, arr=black_stones)
        if len(white_stones) != 0:
            white_stones = np.apply_along_axis(self._decrease_rect, axis=1, arr=white_stones) 

        matrix = np.zeros((self._size, self._size), dtype=int)

        for i in range(self._size):
            for j in range(self._size):
                # координаты основной точки, на которой расположен камень 
                x = self._start[0] + int(i * self._step_x) 
                y = self._start[1] + int(j * self._step_y)

                if self.color_detection:
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
                
                elif self.color_detection and all(component < 100 for component in color):
                    matrix[j][i] = 1

                elif self.color_detection and all(component > 200 for component in color):
                    matrix[j][i] = 2
                    
                if self.debug:
                    yellow = (0, 255, 255)
                    cv2.rectangle(precessed_image, (x,y), (x,y), yellow, 5)
                    if self.color_detection:
                        cv2.rectangle(precessed_image, (x1, y1), (x2, y2), yellow, 2)

                    for x, y, b, h in black_stones:
                        cv2.rectangle(precessed_image, (x, y), (x+b, y+h), yellow, 4)

                    for x, y, b, h in white_stones:
                        cv2.rectangle(precessed_image, (x, y), (x+b, y+h), yellow, 4)
      
        if self.debug:
            self._view_image(precessed_image)

        return matrix  


    def _view_image(self, image, window_name='Result of proccessing'):
        # Создание окна
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 800)
        cv2.imshow(window_name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()