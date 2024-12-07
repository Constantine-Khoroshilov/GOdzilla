import numpy as np
import cv2
import os


class StonesDetection:
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

        self.use_grayscale = False

        if self.use_grayscale:
            cascade_black_path = os.path.join('models_parameters', 'stones_detector', 'black-cascade-grayscale.xml')
            cascade_white_path = os.path.join('models_parameters', 'stones_detector', 'white-cascade-grayscale.xml')
        else:
            cascade_black_path = os.path.join('models_parameters', 'stones_detector', 'black-cascade.xml')
            cascade_white_path = os.path.join('models_parameters', 'stones_detector', 'white-cascade.xml')

        self._cascade_black = cv2.CascadeClassifier(cascade_black_path)
        self._cascade_white = cv2.CascadeClassifier(cascade_white_path)     
        
        self.debug = False


    def _detect(self, src: np.ndarray, cascade: cv2.CascadeClassifier):
        # минимальный размер объектов, которые будут обнаруживаться каскадом
        min_size = (int(self._width / 70), int(self._length / 70))
        rects = cascade.detectMultiScale(src, scaleFactor=1.1, minNeighbors=3, minSize=min_size, flags=cv2.CASCADE_SCALE_IMAGE)

        return [] if len(rects) == 0 else rects


    def get_stones_matrix(self, src: np.ndarray) -> np.ndarray:
        ''' Метод принимает на вход:
                src - открытое исходное изображение игровой доски ГО,                
            и возвращает матрицу расположения 
            камней на изображении.
        '''
        gray_image = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        black_stones = self._detect(gray_image, self._cascade_black)
        white_stones = self._detect(gray_image, self._cascade_white)

        if self.debug:
            processed_image = src.copy()
            for stones in black_stones, white_stones:
                for x, y, w, h in stones:
                    cv2.rectangle(processed_image, (x, y), (x + w, y + h), (0, 255, 255), 3)

        matrix = np.zeros((self._size, self._size), dtype=int)

        for i in range(self._size):
            for j in range(self._size):
                # координаты основной точки, на которой расположен камень 
                x = self._start[0] + int(i * self._step_x) 
                y = self._start[1] + int(j * self._step_y)

                for stone in black_stones:
                    if (stone[0] < x < stone[0] + stone[2]) and (stone[1] < y < stone[1] + stone[3]): 
                        # stones.remove(stone)
                        matrix[j][i] = 1
                        break

                for stone in white_stones:
                    if (stone[0] < x < stone[0] + stone[2]) and (stone[1] < y < stone[1] + stone[3]):  
                        # stones.remove(stone)
                        matrix[j][i] = 2
                        break
                    
                if self.debug:
                    cv2.rectangle(processed_image, (x,y), (x,y), (0, 255, 255), 5)
        
        if self.debug:
            self._view_image(processed_image)

        return matrix  


    def _view_image(self, image, window_name='Result of proccessing'):
        # Создание окна
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 800)
        cv2.imshow(window_name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


