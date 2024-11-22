    let uploadedVideoUrl = null; // Глобальная переменная для хранения URL загруженного видео
    let videoElement; // Переменная для элемента <video>

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
    function openCutVideoPage() {
        const mainElement = document.querySelector('.main');

        if (uploadedVideoUrl) {
            // Подставляем видео и интерфейс обрезки
            // !!! - НЕ ЗНАЮ КАК ВЫНЕСТИ В ОТДЕЛЬНЫЙ .HTML, Т.К НАДО ПЕРЕДАВАТЬ uploadedVideoUrl
            mainElement.innerHTML = 
            `
                <div class="video-player-container">
                    <video controls class="video-player" id="video-player">
                        <source src="${uploadedVideoUrl}" type="video/mp4">
                        Ваш браузер не поддерживает видео.
                    </video>
                </div>
                <div class="slider-container">
                    <div id="video-slider"></div>
                    <div class="time-display">
                        <span>Начало: <span id="start-time">0:00</span></span>
                        <span>Конец: <span id="end-time">0:00</span></span>
                    </div>
                </div>
                <button class="ret-button" onclick="openMain()">Вернуться на главную</button>
                <button id="trim-video-button" class="return-button">Обрезать видео</button>
            `;

            // Устанавливаем событие на ползунок и видео
            videoElement = document.getElementById('video-player');
            videoElement.onloadedmetadata = () => initializeSlider(videoElement.duration);
        } 
        else {
            // Предупреждение, если видео не загружено
            alert('Сначала загрузите видео!'); 
        }
    }

    // Функция для инициализации ползунка
    function initializeSlider(duration) {
        const slider = document.getElementById('video-slider');
        const startTimeElement = document.getElementById('start-time');
        const endTimeElement = document.getElementById('end-time');

        // Создаем ползунок с помощью библиотеки noUiSlider
        noUiSlider.create(slider, {
            start: [0, Math.min(10, duration)], // Начальные позиции ползунков
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
        slider.noUiSlider.on('update', function (values) {
            const [startValue, endValue] = values.map(Number);
            videoStart = startValue;
            videoEnd = endValue;

            // Обновляем отображение времени
            startTimeElement.textContent = formatTime(videoStart);
            endTimeElement.textContent = formatTime(videoEnd);

            // Синхронизируем видео с ползунком
            if (videoElement.currentTime != videoStart) {
                videoElement.currentTime = videoStart;
            } 
            else if (videoElement.currentTime != videoEnd) {
                videoElement.pause();
                videoElement.currentTime = videoStart;
            }
        });
        
        // Нажатие кнопки "Обрезать видео"
        document.getElementById('trim-video-button').onclick = () => {
            trimVideo(videoStart, videoEnd);
            };

        // Обработчик события окончания интервала воспроизведения
        videoElement.addEventListener('timeupdate', () => {
            if (videoElement.currentTime >= videoEnd) {
                videoElement.pause();
                videoElement.currentTime = videoStart;
            }
        });
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
    // !!! - ПОКА ПРОСТО ЗАПИСЫВАЕТ И ОТОБРАЖАЕТ ВРЕМЯ
    function trimVideo(startTime, endTime) {
        alert(`Обрезаем видео от ${startTime} до ${endTime} !`);
        // Добавить логику обрезки видео - !!!
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
