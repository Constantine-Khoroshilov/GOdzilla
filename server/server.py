from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import threading
import aiofiles
import asyncio
import uvicorn
import uuid
import enum
import os



app = FastAPI()

videos_folder = 'videos'
sgfs_folder = 'sgfs'

os.makedirs('static', exist_ok=True)
app.mount('/static', StaticFiles(directory='static'), name='static')

os.makedirs(videos_folder, exist_ok=True)
os.makedirs(sgfs_folder, exist_ok=True)



@app.get('/')
async def root():
    async with aiofiles.open('index.html', encoding='utf-8') as f:
        return HTMLResponse(await f.read())



videos = {}


def generate_video_id():
    while True:
        video_id = str(uuid.uuid4())
        if video_id not in videos:
            return video_id


def exists_video_id(video_id):
    if video_id not in videos:
        raise HTTPException(404, 'The video ID was not found')


class Processing:
    ''' Класс для обработки видеозаписи.

        Этот класс управляет процессом обработки видео, включая 
        проверку готовности видео к обработке, запуск обработки 
        в отдельном потоке и управление статусом обработки.
    '''
    class Status(enum.Enum):
        STOPPED = 'stopped'
        RUNNING = 'running'
        FAILURE = 'failure'

    def __init__(self, video):
        self._video = video
        self.status = Processing.Status.STOPPED
        self.error_message = None

    def run(self):
        ''' Запускает обработку подготовленной видеозаписи в отдельном потоке.
            Если обработка началась вернет True, иначе - False
        '''
        # if not self._is_video_prepared():
        #    return False # видеозапись не подготовлена к обработке

        self._video.status = Video.Status.PROCESSING
        self.status = Processing.Status.RUNNING
        self.error_message = None
        self._start_processing()
        return True

    def stop(self):
        self._video.status = Video.Status.UPLOADED
        self.status = Processing.Status.STOPPED

    class ProcessingCancelled(Exception):
        ''' Исключение, которое возникает при отмене обработки видеофайла '''
        def __init__(self):
            super().__init__('Processing was cancelled')

    def break_processing(self):
        ''' Метод, вызывающий исключение ProcessingCancelled,
            если процесс обработки был остановлен, вызывается 
            только внутри функции обработки видеозаписи
        '''
        if self.status == Processing.Status.STOPPED:
            raise Processing.ProcessingCancelled()

    def _is_video_prepared(self):
        ''' Возвращает True, если видеозапись готова к обработке ''' 
        return (
            self._video.status == Video.Status.UPLOADED and
            self._video.interval is not None and 
            self._video.board_area is not None)

    def to_thread(func):
        ''' Декоратор для запуска функции в отдельном потоке '''
        def wrapper(*args, **kwargs):
            threading.Thread(target=func, args=args, kwargs=kwargs).start()
        return wrapper

    @to_thread
    def _start_processing(self):
        video_name, _ = os.path.splitext(os.path.basename(self._video.path))
        sgf_path = os.path.join(sgfs_folder, f'{video_name}.txt')

        try:
            # функция обработки видеозаписи 
            import time

            for _ in range(5):
                self.break_processing()
                time.sleep(5)

            with open(sgf_path, 'w') as f:
                f.write('Hello George!')
            # конец функции обработки

            self._video.sgf_path = sgf_path
            self._video.status = Video.Status.PROCESSED
            self.status = Processing.Status.STOPPED

        except Processing.ProcessingCancelled:
            if os.path.exists(sgf_path):
                os.remove(sgf_path)

        except Exception as exception:
            self._video.status = Video.Status.UPLOADED
            self.status = Processing.Status.FAILURE
            self.error_message = f'Error: {exception}' 


class Video:
    class Status(enum.Enum):
        NOT_UPLOADED = 'not_uploaded'
        UPLOADING = 'uploading'
        UPLOADED = 'uploaded'
        PROCESSING = 'processing'
        PROCESSED = 'processed'

    class BoardArea:
        def __init__(self, x1, y1, x2, y2):
            self.x1 = x1
            self.x2 = x2
            self.y1 = y1
            self.y2 = y2

    class TimeInterval:
        def __init__(self, start, stop):
            self.start = start
            self.stop = stop

    def __init__(self, video_id):
        self.id = video_id
        self.status = Video.Status.NOT_UPLOADED
        self.path = None
        self.sgf_path = None
        self.interval = None
        self.board_area = None
        self.processing = Processing(self)

    async def remove_file(self):
        ''' Удаляет видеофайл (не объект) '''
        await asyncio.to_thread(os.remove, self.path)
        self.path = None

    def set_board_area(self, x1, y1, x2, y2):
        ''' Задает область игровой доски:
            x1, y1 - левая верхняя точка области
            x2, y2 - правая нижняя точка области
        '''
        self.board_area = Video.BoardArea(x1, y1, x2, y2)

    def set_interval(self, start, stop):
        ''' Указывает начальную и конечную точки (в миллисекундах) 
            временного интервала видеозаписи, который подлежит обработке
        '''
        self.interval = Video.TimeInterval(start, stop)



@app.get('/video_id')
async def get_video_id():
    video = Video(generate_video_id())
    videos[video.id] = video
    return {'video_id': video.id, 'status': video.status}


class UploadingCancelled(Exception):
    ''' Исключение, которое возникает при отмене загрузки видеофайла '''
    def __init__(self):
        super().__init__('Uploading was cancelled')

def upload_request_validator(upload_func):
    ''' Декоратор для проверки правильности запроса перед загрузкой видеофайла '''
    async def upload(video_id: str, file: UploadFile = File(...)):
        exists_video_id(video_id)
        video = videos[video_id]

        if video.status != Video.Status.NOT_UPLOADED:
            raise HTTPException(400, 'The video file has already been uploaded')

        max_size = 32212254720 # 30 GB
        if file.size > max_size:
            raise HTTPException(400, f'The file size is more than {32212254720 // 1024**3} GB')
        
        extensions = {'.mp4', '.mkv', '.mov'}
        _, extension = os.path.splitext(file.filename)
        if extension.lower() not in extensions:
            raise HTTPException(400, 'The extension of the file is not supported')

        return await upload_func(video, file)

    return upload

@app.post('/upload')
@upload_request_validator
async def upload(video, file):
    video.status = Video.Status.UPLOADING
    video.path = os.path.join(videos_folder, f'{video.id}-{file.filename}')
    try:
        async with aiofiles.open(video.path, 'wb') as f:
            while True:
                buffer = await file.read(1048576) # 1 MB
                if not buffer:
                    break

                if video.status != Video.Status.UPLOADING:
                    raise UploadingCancelled()

                await f.write(buffer)

    except UploadingCancelled as exception:
        video.status = Video.Status.NOT_UPLOADED
        await video.remove_file()
        return {'video_id': video.id, 'status': video.status}

    except Exception as exception:
        video.status = Video.Status.NOT_UPLOADED
        await video.remove_file()
        raise HTTPException(500, f'Internal server error: {exception}')

    if video.processing.run():
        return {'video_id': video.id, 'status': video.status}

    video.status = Video.Status.UPLOADED
    return {'video_id': video.id, 'status': video.status}



@app.post('/cancel_uploading')
async def cancel_uploading(video_id: str):
    exists_video_id(video_id)
    video = videos[video_id]
    
    if video.status != Video.Status.UPLOADING:
        raise HTTPException(400, 'The video file is not being uploaded')

    video.status = Video.Status.NOT_UPLOADED
    return {'video_id': video.id, 'status': video.status}



@app.post('/cancel_processing')
async def cancel_processing(video_id: str):
    exists_video_id(video_id)
    video = videos[video_id]
    
    if video.status != Video.Status.PROCESSING:
        raise HTTPException(400, 'The video file is not being processed')

    video.processing.stop()
    return {'video_id': video.id, 'status': video.status}


@app.post('/start_processing')
async def start_processing(video_id: str):
    exists_video_id(video_id)
    video = videos[video_id]
    
    if video.status != Video.Status.UPLOADED:
        raise HTTPException(400, 
            'The video file is being processed, ' + 
            'maybe it has already been processed or ' +
            'it has not yet been uploaded')

    video.processing.run()
    return {'video_id': video.id, 'status': video.status}


@app.get('/get_processing_status')
async def get_processing_status(video_id: str):
    exists_video_id(video_id)
    video = videos[video_id]

    response = {
        'video_id': video.id, 
        'status': video.status, 
        'processing': video.processing.status
    }

    if video.processing.status == Processing.Status.FAILURE:
        response['error'] = video.processing.error_message
    
    return response



@app.get('/download_sgf')
async def download_sgf(video_id: str, file_name: str = None):
    exists_video_id(video_id)
    video = videos[video_id]

    if video.status != Video.Status.PROCESSED:
        raise HTTPException(400, 'The video file has not been processed')

    filename = file_name if file_name is not None else os.path.basename(video.sgf_path)
    return FileResponse(video.sgf_path, filename = filename)


if __name__ == '__main__':
    uvicorn.run(app)