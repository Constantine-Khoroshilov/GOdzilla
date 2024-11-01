from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from enum import Enum
import aiofiles
import asyncio
import uvicorn
import uuid
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


def check_video_id(video_id):
    if video_id is None:
        raise HTTPException(400, 'The video ID is missing')
    if video_id not in videos:
        raise HTTPException(404, 'The video ID was not found')


class Video:
    class Status(Enum):
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
        self.interval = None
        self.board_area = None

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

    def is_not_uploaded(self):
        return self.status == Video.Status.NOT_UPLOADED

    def is_uploading(self):
        return self.status == Video.Status.UPLOADING



@app.get('/video_id')
async def get_video_id():
    video_id = generate_video_id()
    video = Video(video_id)
    videos[video_id] = video
    return {'video_id': video.id, 'status': video.status}




@app.post('/upload')
async def upload(video_id: str = None, file: UploadFile = File(None)):
    async def remove(path):
        await asyncio.to_thread(os.remove, path)

    check_video_id(video_id)
    if file is None:
        raise HTTPException(400, 'The video file is missing')
    
    video = videos[video_id]
    if not video.is_not_uploaded():
        raise HTTPException(400, 'The video file has already been uploaded')

    video.status = Video.Status.UPLOADING
    video_path = os.path.join(videos_folder, f'{video.id}-{file.filename}')
    try:
        async with aiofiles.open(video_path, 'wb') as f:
            while True:
                buffer = await file.read(1048576) # 1 MB
                if not buffer:
                    break

                if not video.is_uploading():
                    await f.close()
                    await remove(video_path)
                    return {'video_id': video.id, 'status': video.status}

                await f.write(buffer)

    except Exception as e:
        await remove(video_path)
        video.status = Video.Status.NOT_UPLOADED
        raise HTTPException(500, f'Internal server error: {e}')

    video.status = Video.Status.UPLOADED
    video.path = video_path

    return {'video_id': video.id, 'status': video.status}



@app.post('/cancel_uploading')
async def cancel_uploading(video_id: str = None):
    check_video_id(video_id)
    video = videos[video_id]
    
    if not video.is_uploading():
        raise HTTPException(400, 'The video file is not being uploaded')

    video.status = Video.Status.NOT_UPLOADED
    return {'video_id': video.id, 'status': video.status}



if __name__ == '__main__':
    uvicorn.run(app)