var uploadedVideoUrl = null; // Глобальная переменная для хранения URL загруженного видео
var videoElement; // Переменная для элемента <video>

var video_id;

var videoStart;
var videoStop;
var videoEnd;

var processing_data = {
    "segment": {
        "start": 0,
        "stop": 0
    },
    "board_area": {
        "x1": 0,
        "y1": 0,
        "x2": 0,
        "y2": 0
    }
}

// Сохраняем оригинальный контент главной страницы
const originalMainContent = document.querySelector('.main').innerHTML;

// Функция для восстановления главной страницы (если мы допустим находимся на "Справка")
function openMain() {
    const mainElement = document.querySelector('.main');
    mainElement.style.display = 'grid';
    mainElement.innerHTML = originalMainContent;
    const cutVideoButton = document.getElementById('cut-video-button'); // Кнопка "Обрезать видео"
    const areabutton = document.getElementById('area-video-button'); // Кнопка "Обрезать видео"
    const resultbutton = document.getElementById('result-video-button'); // Кнопка "Обрезать видео"
    const strelki = document.querySelectorAll('#strelka');
    restoreMainEvents();
}

// Функция для восстановления событий на главной странице
function restoreMainEvents() {
    const cutVideoButton = document.getElementById('cut-video-button'); // Кнопка "Обрезать видео"
    const loadVideoButton = document.getElementById('load-video');
    const manButton = document.getElementById('open-man-button'); // Кнопка справки
    const manButt = document.getElementById('open-man-butt'); // Альтернативная кнопка справки
    const loadingGif = document.getElementById('loading-gif'); // Анимация загрузки

    const areabutton = document.getElementById('area-video-button'); // Кнопка "Обрезать видео"
    const resultbutton = document.getElementById('result-video-button'); // Кнопка "Обрезать видео"
    const strelki = document.querySelectorAll('#strelka');
            
    strelki.forEach(strelka => {
        console.log(strelka); // Каждый найденный элемент
        strelka.style.visibility = 'hidden'; 
    });

    cutVideoButton.style.visibility = 'hidden';
    areabutton.style.visibility = 'hidden';
    resultbutton.style.visibility = 'hidden';

    // Скрыть анимацию загрузки, если она есть
    if (loadingGif) {
        loadingGif.style.display = 'none';
    }


    // Открытие справки на "Главная"
    if (manButton) {
        manButton.onclick = openMan;
    }
    // Открытие справки на навигационной панельке
    if (manButt) {
        manButt.onclick = openMan;
    }

    if (loadVideoButton) {
         loadVideoButton.onclick = loadVideo;
    }

    // Открытие "Обрезка видео"
    if (cutVideoButton) {
        cutVideoButton.onclick = openCutVideoPage;
    }
}

// Функция для открытия страницы обрезки видео
async function openCutVideoPage() {
    const mainElement = document.querySelector('.main');
    const cutVideoButton = document.getElementById('cut-video-button'); // Кнопка "Обрезать видео"
    const areabutton = document.getElementById('area-video-button'); // Кнопка "Обрезать видео"
    const resultbutton = document.getElementById('result-video-button'); // Кнопка "Обрезать видео"
    const strelki = document.querySelectorAll('#strelka');
    areabutton.setAttribute('disabled', '');
    resultbutton.setAttribute('disabled', '');
            
    strelki.forEach(strelka => {
        console.log(strelka); // Каждый найденный элемент
        strelka.style.visibility = 'visible'; 
    });
    cutVideoButton.style.visibility = 'visible';
    cutVideoButton.style.backgroundColor = 'skyblue'
    areabutton.style.visibility = 'visible';
    resultbutton.style.visibility = 'visible';
    areabutton.style.backgroundColor = 'rgb(122, 122, 122)';


    if (uploadedVideoUrl) {
        // Получение статического файла с интерфейсом обрезки видео
        mainElement.innerHTML = await getStaticFileFromServer('video_cut.html');

        // Подстановка атрибута в тег
        srcPtr = mainElement.getElementsByTagName('source')[0];
        srcPtr.setAttribute('src', uploadedVideoUrl);

        // Навешивание обработчика на нажатие кнопки
        btnPtr = mainElement.getElementsByClassName('ret-button')[0];
        btnPtr.onclick = openMain;

        // Устанавливаем событие на ползунок и видео
        videoElement = document.getElementById('video-player');
        videoElement.onloadedmetadata = () => initializeSlider(videoElement.duration);

        // Нажатие кнопки "Обрезать видео"
        document.getElementById('trim-video-button').onclick = () => {
            setStartStopForVideo(uploadedVideoUrl, videoStart, videoStop);
        };

        // Обработчик события окончания интервала воспроизведения
        videoElement.addEventListener('timeupdate', () => {
            if (videoElement.currentTime >= videoEnd) {
                videoElement.pause();
                videoElement.currentTime = videoStart;
            }
        });
    } 
    else {
        // Предупреждение, если видео не загружено
        alert('Сначала загрузите видео!'); 
    }
}

// Функция для инициализации ползунка
function initializeSlider(duration) {
    videoStart = 0;
    videoStop = duration;
    videoEnd = duration;

    slider = document.getElementById('video-slider');
    // Создаем ползунок с помощью библиотеки noUiSlider
    noUiSlider.create(slider, {
        start: [videoStart, videoEnd], // Начальные позиции ползунков
        connect: true,
        range: {
            min: 0,
            max: duration,
        },
        step: 1,
        format: {
            to: value => Math.round(value), // Округляем значения ползунков
            from: value => Number(value),
        },
    });

    // Слушатель события обновления ползунков
    slider.noUiSlider.on('update', (values) => vidmanager(values));
}

function vidmanager(startEndValues){
    const startTimeElement = document.getElementById('start-time');
    const endTimeElement = document.getElementById('end-time');

    const [startValue, endValue] = startEndValues.map(Number);

    let videoCur;
    if (videoStart - startValue != 0){
        videoStart = startValue;
        videoCur = videoStart;
    }
    else if (videoStop - endValue != 0){
        videoStop = endValue;
        videoCur = videoStop;
    }

    // Обновляем отображение времени
    startTimeElement.textContent = formatTime(videoStart);
    endTimeElement.textContent = formatTime(videoStop);

    if (videoCur != undefined)
        videoElement.currentTime = videoCur;
}

// Форматирование времени в формате MM:SS - для вывода на экран пользователя
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60).toString().padStart(2, '0');
    return `${minutes}:${secs}`;
}

// Функция для загрузки видео на сервер - это Костя еще писал
async function uploadVideoToServer(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const idResponse = await fetch('/video_id', { method: 'GET' });
        const id = (await idResponse.json()).video_id;
        video_id = id;
        const response = await fetch(`/upload?video_id=${id}`, {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();
        console.log(JSON.stringify(data));
    } catch (error) {
        throw new Error('Не удалось загрузить видео.');
    }
}

// Открытие страницы справки - ДЖОРДЖ
async function openMan() {
    const mainElement = document.querySelector('.main');

    // Загружаем контент и устанавливаем его
    mainElement.innerHTML = await getStaticFileFromServer('man.html');
    
    // После загрузки меняем display с grid на flex
    mainElement.style.display = 'flow';

}

async function loadVideo() {
    const mainElement = document.querySelector('.main');
    mainElement.innerHTML = await getStaticFileFromServer('video_loading.html');
    const uploadButton = document.getElementById('upload-button'); // Кнопка справки
    const loadingGif = document.getElementById('loading-gif'); // Анимация загрузки
    const videoInput = document.getElementById('video-input'); // Анимация загрузки cut-video-button
    const obrezkaButton = document.getElementById('cut-button');
    const cancelButton = document.getElementById('cancel-button'); // Кнопка "Отменить загрузку"
    mainElement.style.display = 'grid';

    // Скрыть анимацию загрузки, если она есть
    if (loadingGif) {
        loadingGif.style.display = 'none';
    }

    // Настройка события для кнопки загрузки видео
    if (uploadButton && videoInput) {
        // Открываем окно выбора файла
        uploadButton.onclick = () => videoInput.click();

        videoInput.onchange = async function () {
            if (videoInput.files.length > 0) {
                // Сохраняем URL загруженного видео для использования
                uploadedVideoUrl = URL.createObjectURL(videoInput.files[0]);
                console.log('Загружено видео:', uploadedVideoUrl);

                // Меняем отображение кнопки загрузки и справки -> гифка
                uploadButton.style.display = 'none';
                if (loadingGif) loadingGif.style.display = 'block'; // Показываем анимацию загрузки
                if (cancelButton) cancelButton.style.display = 'inline'; // Показываем кнопку "Отменить"


                try {
                    // Загружаем видео на сервер
                    await uploadVideoToServer(videoInput.files[0]);
                } 
                catch (error) {
                    alert('Ошибка при загрузке видео: ' + error.message);
                } 
                finally {
                    obrezkaButton.style.display = 'block';
                    if (cancelButton) cancelButton.style.display = 'none'; // Скрываем кнопку "Отменить"
                    if (loadingGif) loadingGif.style.display = 'none'; // Скрываем анимацию загрузки
                }
            }
        };
    }

    // Настройка события для кнопки "Отменить загрузку"
    if (cancelButton) {
        cancelButton.onclick = loadVideo;
    }

    // Открытие "Обрезка видео"
    if (obrezkaButton) {
        obrezkaButton.onclick = openCutVideoPage;
    }

}

// Загрузка статического файла с сервера - ДЖОРДЖ
async function getStaticFileFromServer(fileName) {
    const response = await fetch(`/static/${fileName}`, { method: 'GET' });
    return response.text();
}


async function getProcessingStatus(video_id) {
    const url = new URL(`http:/127.0.0.1:8000/get_processing_status`);
    url.searchParams.append('video_id', video_id);

    const response = await fetch (url, { method: 'GET' })
    const data = await response.json();
    const status = data.status; 
    return status;
}


async function postProcessingData() {
    const url = new URL(`http:/127.0.0.1:8000/send_processing_data`);
    url.searchParams.append('video_id', video_id);

    const response = await fetch(url, 
        { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(processing_data), 
        }
    );

    if (!response.ok) {
        console.log(JSON.stringify(processing_data))
        throw new Error(`Unknown response: ${response.statusText}`);
    }
    console.log("Processing data sent");

    let status;

    while ((status = await getProcessingStatus(video_id)) !== "processed") {
        console.log(status);
        await new Promise(resolve => setTimeout(resolve, 1000)); // wait for 1 second
    }

    console.log("Processing complete!");
}

async function getSGF(fileName="test_sgf") {
    const url = new URL(`http:/127.0.0.1:8000/download_sgf`);
    url.searchParams.append('video_id', video_id);
    url.searchParams.append('file_name', fileName);

    const response = await fetch(url, { method: 'GET' } );

    if (response.ok)
        console.log(`OK: ${response.text()}`);
    else 
        console.log(`Unknown response: ${response}`);
}

async function openArea(video, start) {
    const mainElement = document.querySelector('.main');
    mainElement.innerHTML = await getStaticFileFromServer('area_select.html');
    const cutVideoButton = document.getElementById('cut-video-button'); // Кнопка "Обрезать видео"
    const areabutton = document.getElementById('area-video-button'); // Кнопка "Обрезать видео"
    const resultbutton = document.getElementById('result-video-button'); // Кнопка "Обрезать видео"
    const strelki = document.querySelectorAll('#strelka');
    // добавляем ей атрибут disabled
    resultbutton.setAttribute('disabled', '');
    strelki.forEach(strelka => {
        console.log(strelka); // Каждый найденный элемент
        strelka.style.visibility = 'visible'; 
    });
    cutVideoButton.style.visibility = 'visible';
    cutVideoButton.style.backgroundColor = 'LightGreen';
    const cutVideoButton_obrezka = document.getElementById('cut-button-obrezka');
    // Открытие "Обрезка видео" из выделения области
    if (cutVideoButton_obrezka) {
        cutVideoButton_obrezka.onclick = openCutVideoPage;
    }

    // Открытие справки на "Главная"
    if (cutVideoButton) {
        cutVideoButton.onclick = openCutVideoPage;
    }

    areabutton.style.backgroundColor = 'skyblue';
    areabutton.style.visibility = 'visible';
    resultbutton.style.visibility = 'visible';


    if (video) {
        // Подстановка атрибута в тег
        srcPtr = mainElement.getElementsByTagName('source')[0];
        srcPtr.setAttribute('src', video);
        video0 = document.getElementById('video0');
        // Устанавливаем начальное время видео
        video0.addEventListener('loadeddata', () => {
            video0.currentTime = start; // Устанавливаем время начала
        });
    } 
    else {
        // Предупреждение, если видео не загружено
        alert('Сначала загрузите видео!'); 
    }
    
    const rectangle = document.getElementById('rectangle');
    const resizer = document.querySelector('.resizer');
    const container = document.getElementById('container');
    const saveButton = document.getElementById('saveButton');
    
    let isResizing = false;
    let isDragging = false;
    let startX, startY, startWidth, startHeight;


    // Get the bounding box of the video (the container's size)
    const getContainerBounds = () => {
        const rect = video0.getBoundingClientRect();
        return {
            width: rect.width,
            height: rect.height,
            left: rect.left,
            top: rect.top
        };
    };

    // Dragging logic
    rectangle.addEventListener('mousedown', (e) => {
        if (e.target !== resizer) {
            isDragging = true;
            startX = e.clientX - rectangle.offsetLeft;
            startY = e.clientY - rectangle.offsetTop;
        }
    });

    document.addEventListener('mousemove', (e) => {
        const containerBounds = getContainerBounds();

        if (isDragging) {
            let x = e.clientX - startX;
            let y = e.clientY - startY;

            // Limit dragging inside container bounds
            x = Math.max(0, Math.min(x, containerBounds.width - rectangle.offsetWidth));
            y = Math.max(0, Math.min(y, containerBounds.height - rectangle.offsetHeight));

            rectangle.style.left = `${x}px`;
            rectangle.style.top = `${y}px`;
        }
        if (isResizing) {
            let newWidth = startWidth + (e.clientX - startX);
            let newHeight = startHeight + (e.clientY - startY);

            // Ensure the rectangle stays inside the video bounds when resizing
            const maxWidth = containerBounds.width - rectangle.offsetLeft;
            const maxHeight = containerBounds.height - rectangle.offsetTop;

            newWidth = Math.max(50, Math.min(newWidth, maxWidth)); // Min and max width
            newHeight = Math.max(50, Math.min(newHeight, maxHeight)); // Min and max height

            rectangle.style.width = `${newWidth}px`;
            rectangle.style.height = `${newHeight}px`;
        }
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
        isResizing = false;
    });

    // Resizing logic
    resizer.addEventListener('mousedown', (e) => {
        isResizing = true;
        startX = e.clientX;
        startY = e.clientY;
        startWidth = rectangle.offsetWidth;
        startHeight = rectangle.offsetHeight;
        e.preventDefault();
    });

    saveButton.addEventListener('click', open_sgf_page)
}

async function open_sgf_page(){
    const rect = rectangle.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();
    const coords = {
        x1: rect.left - containerRect.left,
        y1: rect.top - containerRect.top,
        x2: rect.right - containerRect.left,
        y2: rect.bottom - containerRect.top
    };
    processing_data["board_area"]["x1"] = Math.round(coords.x1);
    processing_data["board_area"]["x2"] = Math.round(coords.x2);
    processing_data["board_area"]["y1"] = Math.round(coords.y1);
    processing_data["board_area"]["y2"] = Math.round(coords.y2);

    alert(`Координаты прямоугольника:\nX1: ${coords.x1}, Y1: ${coords.y1}, X2: ${coords.x2}, Y2: ${coords.y2}`);
    await postProcessingData();
    GetAnswer();   
}


function captureFrameAtTimeAndSave(uploadedVideoURL, start) {
    // Создаем элемент video
    const videoElement = document.createElement('video');
    videoElement.src = uploadedVideoURL;

    // Когда видео готово к воспроизведению
    videoElement.onloadedmetadata = function() {
        // Устанавливаем время видео в заданное значение start
        videoElement.currentTime = start;
    };

    // Когда видео достигло нужного времени (событие seeked)
    videoElement.onseeked = function() {
        // Создаем канвас
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        
        // Устанавливаем размеры канваса в соответствии с размерами видео
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;

        // Рисуем кадр с видео на канвас
        context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

        // Преобразуем канвас в изображение (формат PNG)
        const imageData = canvas.toDataURL('image/png');

        // Создаем ссылку для скачивания
        const link = document.createElement('a');
        link.href = imageData;
        link.download = 'doska.png';  // Название файла
        link.click();  // Имитируем клик для скачивания

        // Очистка
        videoElement.onseeked = null; // Убираем обработчик, чтобы избежать повторного вызова
    };
}

// Обработка обрезки видео
function setStartStopForVideo(uploadedVideoUrl, startTime, endTime) {
    // captureFrameAtTimeAndSave(uploadedVideoUrl, startTime);
    openArea(uploadedVideoUrl, 10);
    alert(`Обрезаем видео от ${formatTime(startTime)} до ${formatTime(endTime)} !`);
    processing_data.segment.start = startTime;
    processing_data.segment.stop = endTime;
}

// ОТВЕЕЕЕЕЕЕЕТ
async function GetAnswer() {
    const mainElement = document.querySelector('.main');
    mainElement.innerHTML = await getStaticFileFromServer('get_sgf.html');
    const cutVideoButton = document.getElementById('cut-video-button'); // Кнопка "Обрезать видео"
    const areabutton = document.getElementById('area-video-button'); // Кнопка "Обрезать видео"
    const resultbutton = document.getElementById('result-video-button'); // Кнопка "Обрезать видео"
    const strelki = document.querySelectorAll('#strelka');
    // добавляем ей атрибут disabled
    resultbutton.setAttribute('disabled', '');
    strelki.forEach(strelka => {
        console.log(strelka); // Каждый найденный элемент
        strelka.style.visibility = 'visible'; 
    });
    cutVideoButton.style.visibility = 'visible';
    cutVideoButton.style.backgroundColor = 'LightGreen';
    const cutVideoButton_obrezka = document.getElementById('cut-button-obrezka');
    
    // Открытие "Обрезка видео" из выделения области
    if (cutVideoButton_obrezka) {
        cutVideoButton_obrezka.onclick = openCutVideoPage;
    }

    if (areabutton) {
        areabutton.onclick = openArea;
    }

    areabutton.style.backgroundColor = 'LightGreen';
    areabutton.style.visibility = 'visible';
    resultbutton.style.visibility = 'visible';
    resultbutton.style.backgroundColor = 'skyblue';

    document.getElementById('get-sgf-button').addEventListener('click', async () => {
        const videoId = video_id; // Замените на ваш актуальный идентификатор видео
        const fileName = video_id + ".sgf"; // Название файла для загрузки
    
        try {
            const response = await fetch(`http://127.0.0.1:8000/download_sgf?video_id=${videoId}&file_name=${fileName}`);
            if (response.ok) {
                const blob = await response.blob();
    
                // Используем File System Access API
                const options = {
                    suggestedName: fileName,
                    types: [
                        {
                            description: 'SGF Files',
                            accept: { 'application/vnd.gosu': ['.sgf'] },
                        },
                    ],
                };
    
                // Открываем диалог выбора файла
                const fileHandle = await window.showSaveFilePicker(options);
    
                // Записываем данные в файл
                const writableStream = await fileHandle.createWritable();
                await writableStream.write(blob);
                await writableStream.close();
    
                alert("Файл успешно сохранён!");
            } else {
                alert("Ошибка при загрузке файла: " + response.statusText);
            }
        } catch (error) {
            alert("Ошибка: " + error.message);
        }
    });
}

 // Функция для управления меню
 function toggleMenu() {
    const body = document.body;
    const navi = document.querySelector('.navi');
    navi.classList.toggle('show');
    body.classList.toggle('menu-open');
}

// Восстановление событий при загрузке страницы - ЧТОБЫ ВСЕ КНОПКИ РАБОТАЛИ ПРИ ЗАПУСКЕ
document.addEventListener('DOMContentLoaded', () => {
    restoreMainEvents();
});
