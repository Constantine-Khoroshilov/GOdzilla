const uploadButton = document.getElementById('upload-button');
const videoInput = document.getElementById('video-input');

manButton = document.getElementById('open-man-button');
manButton.onclick = openMan;

async function openMan(){
    let body = document.getElementsByClassName('main')[0];
    body.innerHTML = await getStaticFileFromServer('man.html');
}


uploadButton.onclick = function(){
    videoInput.click()
}

async function uploadVideoToServer(file) {

    const formData = new FormData();
    formData.append('file', file);

    try {
        const idResponse = await fetch('/video_id', { method: 'GET' });
        const id = (await idResponse.json()).video_id;

        const response = await fetch(`/upload?video_id=${id}`, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        alert('Видео успешно загружено!');
        console.log(JSON.stringify(data));

    } catch (error) {
        alert(error);
    }
};

async function getStaticFileFromServer(fileName) {
    let staticFile = await fetch(`/static/${fileName}`, { method: 'GET'}).then(response => response.text());
    return staticFile;
}

videoInput.onchange = function() {
    if (videoInput.files.length > 0) {
        uploadVideoToServer(videoInput.files[0]);
    }
};