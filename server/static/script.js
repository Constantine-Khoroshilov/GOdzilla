    var uploadedVideoUrl = null; // Глобальная переменная для хранения URL загруженного видео
    var videoElement; // Переменная для элемента <video>

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
        mainElement.innerHTML = originalMainContent;
        restoreMainEvents();
    }

    // Функция для восстановления событий на главной странице
    function restoreMainEvents() {
        const cutVideoButton = document.getElementById('cut-video-button'); // Кнопка "Обрезать видео"
        const uploadButton = document.getElementById('upload-button'); // Кнопка "Загрузить видео"
        const videoInput = document.getElementById('video-input'); // Поле для выбора файла видео
        const manButton = document.getElementById('open-man-button'); // Кнопка справки
        const manButt = document.getElementById('open-man-butt'); // Альтернативная кнопка справки
        const loadingGif = document.getElementById('loading-gif'); // Анимация загрузки

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
                    if (manButton) manButton.style.display = 'none';
                    if (loadingGif) loadingGif.style.display = 'block'; // Показываем анимацию загрузки

                    try {
                        // Загружаем видео на сервер
                        await uploadVideoToServer(videoInput.files[0]);
                    } 
                    catch (error) {
                        alert('Ошибка при загрузке видео: ' + error.message);
                    } 
                    finally {
                        // <- восстанавливаем отображение кнопки загрузки
                        uploadButton.style.display = 'block';
                        if (manButton) manButton.style.display = 'block';
                        if (loadingGif) loadingGif.style.display = 'none'; // Скрываем анимацию загрузки
                    }
                }
            };
        }

        // Открытие справки на "Главная"
        if (manButton) {
            manButton.onclick = openMan;
        }
        // Открытие справки на навигационной панельке
        if (manButt) {
            manButt.onclick = openMan;
        }

        // Открытие "Обрезка видео"
        if (cutVideoButton) {
            cutVideoButton.onclick = openCutVideoPage;
        }
    }

    // Функция для открытия страницы обрезки видео
    async function openCutVideoPage() {
        const mainElement = document.querySelector('.main');

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
                setStartStopForVideo(videoStart, videoStop);
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

            const response = await fetch(`/upload?video_id=${id}`, {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            alert('Видео успешно загружено!');
            console.log(JSON.stringify(data));
        } catch (error) {
            throw new Error('Не удалось загрузить видео.');
        }
    }

    // Открытие страницы справки - ДЖОРДЖ
    async function openMan() {
        const mainElement = document.querySelector('.main');
        mainElement.innerHTML = await getStaticFileFromServer('man.html');
    }

    // Загрузка статического файла с сервера - ДЖОРДЖ
    async function getStaticFileFromServer(fileName) {
        const response = await fetch(`/static/${fileName}`, { method: 'GET' });
        return response.text();
    }

    // Обработка обрезки видео
    function setStartStopForVideo(startTime, endTime) {
        alert(`Обрезаем видео от ${formatTime(startTime)} до ${formatTime(endTime)} !`);
        processing_data.segment.start = startTime;
        processing_data.segment.stop = endTime;
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
