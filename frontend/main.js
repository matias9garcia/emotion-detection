$( document ).ready(function() {

    var valueArray = []

    function fetchData(){
        // profe, estoy usando el archivo json local. No pude probarlo con el arduino antes de enviarlo
        // sin embargo, antes de terminar de programar el PPG, estaba usando este endpoint

        // lo malo es que sin la lectura de datos, esta funcion no puede generar el json nuevo
        // asi que lo dejare asi por mientras
        // $.get('http://localhost:5100/analyze', function(data){
        $.getJSON('analyze.json', function(data){ 
               
            var signal_list = data.signal;
            var largo_signal = signal_list.length

            // Lista con el valor de la señal en el tiempo
            // console.log( signal_list );

            for (var i=0; i < largo_signal; i++){
                value = signal_list[i].value
                valueArray.push(value);
            } 

            crearEjes(valueArray);
        });
    }

    function crearEjes(valueArray){

        // Primero, verifica si hay un gráfico existente
        if (window.miGrafico) {
            // Si hay un gráfico existente, destrúyelo
            window.miGrafico.destroy();
        }

        var yValues = valueArray;
        var largo_data = valueArray.length;

        const xValues = []
        for (var i=1; i <= largo_data; i++){
            xValues.push(i);
        }

        window.miGrafico = new Chart("PPG_monitor", {
            type: "line",
            data: {
                    labels: xValues,
                    datasets: [{
                    backgroundColor:"rgba(0,0,255,1.0)",
                    borderColor: "rgba(0,0,255,0.1)",
                    data: yValues
                    }]
                }
        });

    }

    function escribirValoresEmociones(){
        // Cargar el archivo JSON usando AJAX
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
            var jsonString = JSON.parse(xhr.responseText);
                if(jsonString.length < 5){
                    document.getElementById("emotion_score_camera").innerHTML = "Intente de nuevo!"
                    emotion_valence = ""
                }
                else {
                    var jsonObject = JSON.parse(jsonString)
                    var score = jsonObject["0"].score;
                    document.getElementById("emotion_score_camera").innerHTML += score.toString();
                    var emotion_camera = jsonObject["0"].emotion;
                    document.getElementById("emotion_recognized_camera").innerHTML += emotion_camera.toString();

                    if(emotion_camera.toString() == "happy"){
                        arousal_icon = document.getElementById("valence_3")
                        arousal_icon.style.color = "green";
                    } else if(emotion_camera.toString() == "neutral") {
                        arousal_icon = document.getElementById("valence_2")
                        arousal_icon.style.color = "blue";
                    } else if(emotion_camera.toString() == "sad") {
                        arousal_icon = document.getElementById("valence_1")
                        arousal_icon.style.color = "red";
                    } else if(emotion_camera.toString() == "angry") {
                        arousal_icon = document.getElementById("valence_1")
                        arousal_icon.style.color = "red";
                    } else if(emotion_camera.toString() == "fear") {
                        arousal_icon = document.getElementById("valence_1")
                        arousal_icon.style.color = "red";
                    } 
                }
            }
        };
        xhr.open("GET", "emotions.json", true);
        xhr.send();
    }

    function escribirValoresEmocionesPPG(){
        // Cargar el archivo JSON usando AJAX
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
            var jsonObject = JSON.parse(xhr.responseText);
                if(jsonObject.length < 5){
                    document.getElementById("emotion_score_ppg").innerHTML = "Intente de nuevo!"
                    emotion_arousal = ""
                }
                else {
                    // Extraer los valores de "emotion", "heart_rate" y "hrv"
                    var emotion = jsonObject.features.emotion;
                    var heartRate = jsonObject.features.heart_rate;
                    var hrv = jsonObject.features.hrv;

                    //var jsonObject = JSON.parse(jsonString)
                    // var score = jsonObject["0"].score;
                    document.getElementById("heartrate_ppg").innerHTML += heartRate.toString();
                    document.getElementById("hrv_ppg").innerHTML += hrv.toString();
                    // var score = jsonObject["0"].emotion;
                    document.getElementById("emotion_recognized_ppg").innerHTML += emotion.toString();

                    if(heartRate < 50){
                        arousal_icon = document.getElementById("arousal_1")
                        arousal_icon.style.color = "orange";
                    } else if(heartRate > 50 && heartRate < 100) {
                        arousal_icon = document.getElementById("arousal_2")
                        arousal_icon.style.color = "green";
                    } else {
                        arousal_icon = document.getElementById("arousal_3")
                        arousal_icon.style.color = "red";
                    }
                        
                }
            }
        };
        xhr.open("GET", "analyze.json", true);
        xhr.send();
    }

 

    // MAIN EXECUTE LINE

    // Verificar actualizaciones cada 5 segundos
    // setInterval(fetchData, 2000);
    fetchData();
    escribirValoresEmociones();
    escribirValoresEmocionesPPG();


});

document.addEventListener("DOMContentLoaded", function() {
    const video = document.getElementById('video');
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    const captureButton = document.getElementById('captureButton');

    // Solicitar acceso a la cámara
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(err => {
            console.error('Error al acceder a la cámara: ', err);
        });

    // Establecer el tamaño del canvas al tamaño del video
    video.addEventListener('loadedmetadata', function() {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
    });

    // Capturar la foto cuando se presione el botón
    captureButton.addEventListener('click', function(event) {

        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataURL = canvas.toDataURL('image/jpeg');

        $.ajax({
            type: 'POST',
            url: 'http://localhost:5100/predict',
            contentType: 'application/json',
            data: JSON.stringify({ image: dataURL }),  // Suponiendo que imageData contiene los datos de la imagen
            success: function(response) {
                console.log(response);  // Maneja la respuesta aquí
            },
            error: function(xhr, status, error) {
                console.error(error);  // Maneja los errores aquí
            }
        });

        // Prevenir el comportamiento predeterminado del botón. No pude evitar que se recargue la pagina, pero tiene que funcionar de otra manera!!!!
        event.preventDefault();
    });

});


