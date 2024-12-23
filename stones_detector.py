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
        self._lt_x = x1
        self._lt_y = y1
        self._rb_x = x2
        self._rb_y = y2

        self._height = y2 - y1
        self._width = x2 - x1
        
        cascades_folder = os.path.join('models_parameters', 'stones_detector')
        self._black_cascade = cv2.CascadeClassifier(os.path.join(cascades_folder, 'black-cascade-grayscale.xml'))
        self._white_cascade = cv2.CascadeClassifier(os.path.join(cascades_folder, 'white-cascade-grayscale.xml'))
        
        self.debug = False


    def _detect_stones(self, src: np.ndarray, cascade: cv2.CascadeClassifier):
        min_size = (self._width // self._size, self._height // self._size)
        rects = cascade.detectMultiScale(
            src, 
            scaleFactor=1.1, 
            minNeighbors=3, 
            minSize=min_size, 
            flags=cv2.CASCADE_SCALE_IMAGE)

        return rects


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


    def get_stones_matrix(self, src: np.ndarray) -> np.ndarray:
        ''' Метод принимает на вход:
                src - открытое исходное изображение игровой доски ГО,                
            и возвращает матрицу расположения 
            камней на изображении.
        '''
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
        for row in matrix:
            print(row)

        return matrix  


    def _view_image(self, image, window_name='Result of proccessing'):
        # Создание окна
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 800)
        cv2.imshow(window_name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()