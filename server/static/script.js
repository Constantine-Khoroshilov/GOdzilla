// Сохраняем изначальное содержимое элемента с классом "main"
const originalMainContent = document.querySelector('.main').innerHTML;

// Функция для восстановления главной страницы
function openMain() {
    const mainElement = document.querySelector('.main');
    mainElement.innerHTML = originalMainContent;
    // Восстанавливаем события для кнопок после восстановления содержимого
    restoreMainEvents();
}

// Функция для установки событий на кнопки
function restoreMainEvents() {
    const uploadButton = document.getElementById('upload-button');
    const videoInput = document.getElementById('video-input');
    const manButton = document.getElementById('open-man-button');
    const manButt = document.getElementById('open-man-butt');
    const loadingGif = document.getElementById('loading-gif');

    // Скрываем гифку по умолчанию ###
    if (loadingGif) {
        loadingGif.style.display = 'none';
    }

    if (uploadButton && videoInput) {
        uploadButton.onclick = () => videoInput.click();

        videoInput.onchange = async function () {
            if (videoInput.files.length > 0) {
                // Показываем гифку и скрываем кнопки
                uploadButton.style.display = 'none';
                if (manButton) manButton.style.display = 'none';
                if (loadingGif) loadingGif.style.display = 'block';

                try {
                    await uploadVideoToServer(videoInput.files[0]);
                } catch (error) {
                    alert('Ошибка при загрузке видео: ' + error.message);
                } finally {
                    // Восстанавливаем элементы после загрузки
                    uploadButton.style.display = 'block';
                    if (manButton) manButton.style.display = 'block';
                    if (loadingGif) loadingGif.style.display = 'none';
                }
            }
        };
    }

    if (manButton) {
        manButton.onclick = openMan;
    }

    if (manButt) {
        manButt.onclick = openMan;
    }
}

// Функция для открытия справки
async function openMan() {
    const mainElement = document.querySelector('.main');
    mainElement.innerHTML = await getStaticFileFromServer('man.html');
}

// Функция для загрузки видео на сервер
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

// Функция для получения статического файла с сервера
async function getStaticFileFromServer(fileName) {
    const response = await fetch(`/static/${fileName}`, { method: 'GET' });
    return response.text();
}

// Восстановление начальных событий
restoreMainEvents();

// Функция для управления меню
function toggleMenu() {
    const body = document.body;
    const navi = document.querySelector('.navi');
    navi.classList.toggle('show');
    body.classList.toggle('menu-open');
}
