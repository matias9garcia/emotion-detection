from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import numpy as np
import json
from scipy.signal import find_peaks
import datetime

import base64
import os, sys
import subprocess


app = Flask(__name__)
CORS(app)

# Almacenar los datos recibidos
ppg_data = []
timestamps = []

# Importa tu módulo Python
import reconocimiento_emociones_imagen

@app.route('/data', methods=['GET'])
def receive_data():
    value = request.args.get('value', type=int)
    print(value)
    if value is not None:
        ppg_data.append(value)
        timestamps.append(datetime.datetime.now())
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "error"}), 400

@app.route('/analyze', methods=['GET'])
def analyze_data():
    if len(ppg_data) < 100:
        return jsonify({"status": "error", "message": "Not enough data"}),400

    # Convertir lista a array numpy
    ppg_signal = np.array(ppg_data)

    # Filtrado de media móvil
    def moving_average(signal, window_size):
        return np.convolve(signal, np.ones(window_size)/window_size, mode='valid')

    # Aplicar filtro
    filtered_signal = moving_average(ppg_signal, window_size=5)

    # Detectar picos
    peaks, _ = find_peaks(filtered_signal, distance=50) # Ajusta el parámetro 'distance' según tu señal

    # Calcular intervalos entre picos (en muestras)
    peak_intervals = np.diff(peaks)

    # Convertir intervalos a tiempo (asumiendo una frecuencia de muestreo de 100 Hz)
    sampling_rate = 100 # Hz
    peak_intervals_time = peak_intervals / sampling_rate

    timestamps = [datetime.datetime.now() +
    datetime.timedelta(seconds=i / sampling_rate) for i in range(len(filtered_signal))]

    # Crear una lista de diccionarios con timestamps y valores filtrados
    data = [{"timestamp": ts.isoformat(), "value": float(val)} for ts, val in zip(timestamps, filtered_signal)]

    # Calcular frecuencia cardíaca en BPM
    heart_rate = 60 / np.mean(peak_intervals_time)

    # Calcular HRV (Desviación estándar de los intervalos RR)
    hrv = np.std(peak_intervals_time)

    # Calcular amplitud de los picos
    peak_amplitudes = filtered_signal[peaks]
    mean_amplitude = np.mean(peak_amplitudes)
    std_amplitude = np.std(peak_amplitudes)
    max_interval = max(ppg_data)
    min_interval = min(ppg_data)

    if heart_rate < 50:
        emotion="Muy relajado"
    elif 50 <= heart_rate <= 90:
        emotion="Relajado"
    else:
        emotion="Estrés o ansiedad"

    # Compilar características en un diccionario
    features = {
    'heart_rate': heart_rate,
    'hrv': hrv,
    'mean_amplitude': mean_amplitude,
    'std_amplitude': std_amplitude,
    'max':max_interval,
    'min':min_interval,
    'emotion':emotion
    }

    # Exportar características y señal filtrada a un archivo JSON
    output_data = {
    'features': features,
    'signal': data,
    'peaks': peaks.tolist()
    }

    with open('ppg_data.json', 'w') as f:
        json.dump(output_data, f, indent=4)

    print("Características extraídas:", features)

    with open('ppg_data.json', 'w') as f:
        json.dump(output_data, f, indent=4)

    return jsonify(output_data), 200

@app.route('/predict', methods=['POST'])
def save_image():
    data = request.json.get('image')
    if data:
        try:
            # Decodificar la imagen desde base64
            image_data = base64.b64decode(data.split(',')[1])

            # ejecutar el procesamiento de la imagen y la prediccion de la emocion. Este metodo tambien guarda una nueva imagen en la carpeta /generates_images
            try: 
                output = reconocimiento_emociones_imagen.process(image_data)
                
            except Exception as e:
                print(e)
            #print(jsonify({"data": output}))

            # Convertir el diccionario a formato JSON
            json_data = json.dumps(output, indent=4)
            
            # Crear un archivo temporal en memoria
            filename = "frontend/emotions.json"
            with open(filename, "w") as f:
                f.write(json_data)
            
            return jsonify({"message": "Imagen guardada correctamente", "data": output}), 200
        except Exception as e:
            print(e)
            #return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Datos de imagen no proporcionados"}), 400
    
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5100)