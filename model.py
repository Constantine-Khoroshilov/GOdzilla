from ProcessVideo import process_video
from pydantic import BaseModel
from typing import List
from enum import Enum
import threading
import asyncio
import uuid
import os



sgfs_folder = 'sgfs'
os.makedirs(sgfs_folder, exist_ok=True)



videos = {}


def generate_video_id():
    while True:
        video_id = str(uuid.uuid4())
        if video_id not in videos:
            return video_id


def exists_video_id(video_id):
    return video_id in videos

    
def to_thread(func):
    ''' Декоратор для запуска функции в отдельном потоке '''
    def wrapper(*args, **kwargs):
        threading.Thread(target=func, args=args, kwargs=kwargs).start()
    return wrapper


class ProcessingCancelled(Exception):
    ''' Исключение, которое возникает при отмене обработки видеофайла '''
    def __init__(self):
        super().__init__('Processing was cancelled')


class Processing:
    ''' Управляет обработкой видеозаписи, включая запуск, 
        остановку и проверку статуса, а также обработку 
        ошибок и запись результатов
    '''
    class Status(Enum):
        STOPPED = 'stopped'
        RUNNING = 'running'
        FAILURE = 'failure'
        SUCCESS = 'success'

    def __init__(self, video):
        self._video = video
        self.status = Processing.Status.STOPPED
        self.error_message = None
        self.sgf_path = None

    def run(self):
        ''' Запускает обработку подготовленной видеозаписи в отдельном потоке.
            Если обработка началась вернет True, иначе - False
        '''
        if not self._is_video_prepared():
           return False

        self._video.status = Video.Status.PROCESSING
        self.status = Processing.Status.RUNNING
        self.error_message = None
        self._start_processing()
        return True

    def stop(self):
        self._video.status = Video.Status.UPLOADED
        self.status = Processing.Status.STOPPED

    def break_processing(self):
        ''' Метод, вызывающий исключение ProcessingCancelled,
            если процесс обработки был остановлен, вызывается 
            только внутри функции обработки видеозаписи
        '''
        if self.status == Processing.Status.STOPPED:
            raise ProcessingCancelled()

    def _is_video_prepared(self):
        ''' Возвращает True, если видеозапись готова к обработке ''' 
        return (
            self._video.status != Video.Status.NOT_UPLOADED and
            self._video.status != Video.Status.UPLOADING and
            self._video.segment is not None and 
            self._video.board_area is not None)

    @to_thread
    def _start_processing(self):
        video_name, _ = os.path.splitext(os.path.basename(self._video.path))
        self.sgf_path = os.path.join(sgfs_folder, f'{video_name}.sgf')
        try:
            # функция обработки видеозаписи 
            process_video(self._video, self, self.sgf_path)
            # конец функции обработки

            self._video.status = Video.Status.PROCESSED
            self.status = Processing.Status.SUCCESS

        except ProcessingCancelled:
            if os.path.exists(self.sgf_path):
                os.remove(self.sgf_path)
                self.sgf_path = None

        except Exception as exception:
            self._video.status = Video.Status.UPLOADED
            self.status = Processing.Status.FAILURE
            self.error_message = f'Error: {exception}' 



class Video:
    ''' Представляет видеозапись, хранит информацию о статусе, пути, 
        временном интервале и области доски
    '''
    class Status(Enum):
        NOT_UPLOADED = 'not_uploaded'
        UPLOADING = 'uploading'
        UPLOADED = 'uploaded'
        PROCESSING = 'processing'
        PROCESSED = 'processed'

    class Segment(BaseModel):
        ''' Подлежащий обработке отрезок видеозаписи
        '''
        start: int
        stop: int

    class BoardArea(BaseModel):
        x1: int
        y1: int
        x2: int
        y2: int
        
    def __init__(self, video_id):
        self.id = video_id
        self.status = Video.Status.NOT_UPLOADED
        self.path = None
        self.segment = None
        self.board_area = None
        self.processing = Processing(self)

    async def remove(self):
        ''' Удаляет видеофайл (не объект) '''
        await asyncio.to_thread(os.remove, self.path)
        self.path = None



def get_video_by_id(video_id: str = None):
    ''' Функция возвращает объект класса Video по его video_id
        или создает новый, если параметр video_id не передан
    '''
    if video_id is None:
        video = Video(generate_video_id())
        videos[video.id] = video
        return video
    
    return videos[video_id]