from model import Video, Processing, get_video_by_id, exists_video_id
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import aiofiles
import uvicorn
import os



app = FastAPI()

os.makedirs('static', exist_ok=True)
app.mount('/static', StaticFiles(directory='static'), name='static')

videos_folder = 'videos'
os.makedirs(videos_folder, exist_ok=True)



@app.get('/')
async def root():
    async with aiofiles.open('index.html', encoding='utf-8') as f:
        return HTMLResponse(await f.read())


def fetch_video(video_id):
    if not exists_video_id(video_id):
        raise HTTPException(404, 'The video ID was not found')
    return get_video_by_id(video_id)


@app.get('/video_id')
async def get_video_id():
    video = get_video_by_id()
    return {'video_id': video.id, 'status': video.status}


class UploadingCancelled(Exception):
    ''' Исключение, которое возникает при отмене загрузки видеофайла '''
    def __init__(self):
        super().__init__('Uploading was cancelled')

def upload_request_validator(upload_func):
    ''' Декоратор для проверки правильности запроса перед загрузкой видеофайла '''
    async def upload(video_id: str, file: UploadFile = File(...)):
        video = fetch_video(video_id)

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
        await video.remove()
        return {'video_id': video.id, 'status': video.status}

    except Exception as exception:
        video.status = Video.Status.NOT_UPLOADED
        await video.remove()
        raise HTTPException(500, f'Internal server error: {exception}')
    
    video.status = Video.Status.UPLOADED
    video.processing.run()
    return {'video_id': video.id, 'status': video.status}



class ProcessingData(BaseModel):
    segment: Video.Segment
    board_area: Video.BoardArea

@app.post('/send_processing_data')
async def send_processing_data(video_id: str, data: ProcessingData):
    video = fetch_video(video_id)

    if video.status == Video.Status.PROCESSING:
        raise HTTPException(400, 'The video file is being processed')

    video.segment = data.segment
    video.board_area = data.board_area

    video.processing.run()
    return {'video_id': video.id, 'status': video.status}



@app.post('/cancel_uploading')
async def cancel_uploading(video_id: str):
    video = fetch_video(video_id)
    
    if video.status != Video.Status.UPLOADING:
        raise HTTPException(400, 'The video file is not being uploaded')

    video.status = Video.Status.NOT_UPLOADED
    return {'video_id': video.id, 'status': video.status}



@app.post('/cancel_processing')
async def cancel_processing(video_id: str):
    video = fetch_video(video_id)
    
    if video.status != Video.Status.PROCESSING:
        raise HTTPException(400, 'The video file is not being processed')

    video.processing.stop()
    return {'video_id': video.id, 'status': video.status}



@app.get('/get_processing_status')
async def get_processing_status(video_id: str):
    video = fetch_video(video_id)

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
    video = fetch_video(video_id)

    if video.status != Video.Status.PROCESSED:
        raise HTTPException(400, 'The video file has not been processed')

    sgf_name = os.path.basename(video.processing.sgf_path)
    filename = f'{file_name}.txt' if file_name is not None else sgf_name

    return FileResponse(video.processing.sgf_path, filename = filename)



if __name__ == '__main__':
    uvicorn.run(app)