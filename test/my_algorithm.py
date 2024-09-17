import cv2
import numpy as np
import math


def viewImage(image, name_of_window='Some window'):
    cv2.namedWindow(name_of_window, cv2.WINDOW_NORMAL)
    cv2.imshow(name_of_window, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def get_binary_image(src: np.ndarray, thresh: int=150, maxval: int=255) -> np.ndarray:
    ''' Функция принимает на вход:
            src - открытое исходное изображение игровой доски ГО,
            thresh - пороговое значение,
            maxval - итоговый цвет пикселей, текущий цвет к-ых превосходит порог
    '''
    _, binary_image = cv2.threshold(src, thresh, maxval, cv2.THRESH_BINARY)

    return binary_image 


def get_mat_coords(src: np.ndarray, start: tuple, size: int=19) -> np.ndarray:
    ''' Функция принимает на вход:
            src - открытое исходное изображение игровой доски ГО,
            start - координаты пикселя — начало (точка О), относительно
                которого вычисляются координаты камней,  
            size - размерность матрицы (доски)
        и возвращает матрицу расположения 
        камней на изображении.
    '''
    height = src.shape[0]
    width = src.shape[1]

    # переход к RGB
    rgb_image = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
    # простое размытие (сглаживание)
    blurred_image = cv2.blur(rgb_image, (10, 10))
    # пороговая обработка
    binary_image = get_binary_image(blurred_image)

    matrix = [ ['.'] * size for i in range(size) ]

    step_y = (height - 1) / (size - 1)
    step_x = (width - 1) / (size - 1)

    output = binary_image.copy()

    for i in range(size):
        for j in range(size):
            x = int(i * step_x)
            y = int(j * step_y)

            color = binary_image[y, x]

            if (color[0] < 100) and (color[1] < 100) and (color[2] < 100):
                matrix[j][i] = 'X'

            elif (color[0] > 200) and (color[1] > 200) and (color[2] > 200):
                matrix[j][i] = 'O'

            cv2.rectangle(output, (x,y), (x,y), (0, 255, 255), 5)

    viewImage(output, 'test')

    return matrix

size = 19
image = cv2.imread("Image10.jpg")
mat = get_mat_coords(image, (0, 0), size)

for i in range(size):
    print(*mat[i], sep=' ')


