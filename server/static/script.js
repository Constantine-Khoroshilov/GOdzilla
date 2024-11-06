const uploadButton = document.getElementById('uploadButton');
const videoInput = document.getElementById('videoInput');


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

videoInput.onchange = function() {
    if (videoInput.files.length > 0) {
        uploadVideoToServer(videoInput.files[0]);
    }
};