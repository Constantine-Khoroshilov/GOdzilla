import cv2
import numpy as np


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
            size - размерность матрицы (доски).                
        '''
        self._size = size
        self._start = (y1, x1)
        self._end = (y2, x2)
        # высота и ширина игровой доски (области на изображении)
        self._height = y2 - y1
        self._width = x2 - x1
        # разность координат центров камней на доске (в проекциях на оси Y и X)
        self._step_y = (self._height - 1) / (self._size - 1)
        self._step_x = (self._width - 1) / (self._size - 1)
        # размеры области, в которой расположен камень (в проекциях на оси Y и X)
        self._ry = int(0.05 * self._step_y)
        self._rx = int(0.05 * self._step_x)
        # режим отладки
        self.debugging = False
    

    def _get_binary_image(self, src: np.ndarray, thresh: int=140, maxval: int=255) -> np.ndarray:
        ''' Метод принимает на вход:
                src - открытое исходное изображение игровой доски ГО,
                thresh - пороговое значение,
                maxval - итоговый цвет пикселей, текущий цвет к-ых превосходит порог
        '''
        _, binary_image = cv2.threshold(src, thresh, maxval, cv2.THRESH_BINARY)

        return binary_image


    def get_stones_matrix(self, src: np.ndarray) -> np.ndarray:
        ''' Метод принимает на вход:
                src - открытое исходное изображение игровой доски ГО,                
            и возвращает матрицу расположения 
            камней на изображении.
        '''
        # переход к RGB
        rgb_image = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
        # простое размытие (сглаживание)
        # blurred_image = cv2.blur(rgb_image, (30, 30))
        blurred_image = cv2.GaussianBlur(rgb_image, (51, 51), 0)
        # пороговая обработка
        binary_image = self._get_binary_image(blurred_image)

        matrix = np.array( [ [0] * self._size for i in range(self._size) ] )
        
        if self.debugging:
            # создает изображение для отладки
            output = binary_image.copy()

        for i in range(self._size):
            for j in range(self._size):
                # координаты центра камня 
                x = self._start[0] + int(i * self._step_x) 
                y = self._start[1] + int(j * self._step_y)
                
                # средний цвет области, в которой расположен камень
                upper_border = y - self._ry if (y - self._ry) > self._start[0] else y
                botom_border = y + self._ry if (y + self._ry) < self._end[0] else y
                left_border  = x - self._rx if (x - self._rx) > self._start[1] else x
                right_border = x + self._rx if (x + self._rx) < self._end[1] else x
                
                colors = binary_image[
                    upper_border : botom_border, 
                    left_border : right_border
                ]
                color = cv2.mean(colors)[:3]
                
                if all(component < 100 for component in color):
                    matrix[j][i] = 1

                elif all(component > 200 for component in color):
                    matrix[j][i] = 2
                    
                if self.debugging:
                    # добавление желтой сетки на изображение для отладки 
                    yellow = (0, 255, 255)
                    cv2.rectangle(output, (x,y), (x,y), yellow, 5)
                    cv2.rectangle(output, (left_border, upper_border), (right_border, botom_border), yellow, 2)
        
        if self.debugging:
            # показ изображения для отладки
            self._view_image(output)

        return matrix  


    def _view_image(self, image, window_name='Result of proccessing'):
        # Создает окно
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 800)
        # Отображает изображение в окне
        cv2.imshow(window_name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


