import sys

import cv2

import h5py
import tensorflow as tf
from tensorflow.keras.models import load_model
import base64
import numpy as np
from PIL import Image
import io

from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.inference import load_image
from utils.preprocessor import preprocess_input

import json

def process(image_data):

    # Ejemplo de bytes de una imagen

    # Convertir los bytes a una imagen PIL
    image = Image.open(io.BytesIO(image_data))

    # Convertir la imagen PIL a un numpy array
    rgb_image = np.array(image)

    # Convertir la imagen RGB a una imagen en blanco y negro
    image_bw = image.convert('L')
    image_bw_array = np.array(image_bw)

    # # Mostrar las dimensiones y tipos de las imágenes resultantes
    # print(f"RGB image shape: {rgb_image.shape}, dtype: {rgb_image.dtype}")
    # print(f"Black and white image shape: {image_bw_array.shape}, dtype: {image_bw_array.dtype}")


    #print(type(image_data))
    image_path = 'received_images/captura.jpg'
    detection_model_path = 'face_classification/trained_models/detection_models/haarcascade_frontalface_default.xml'
    emotion_model_path = 'face_classification/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'

    # face_classification\
    emotion_labels = get_labels('fer2013')
    font = cv2.FONT_HERSHEY_SIMPLEX

        # hyper-parameters for bounding boxes shape
    emotion_offsets = (20, 40)
    emotion_offsets = (0, 0)

        # loading models
    face_detection = load_detection_model(detection_model_path)
    emotion_classifier = load_model(emotion_model_path, compile=False)

        # getting input model shapes for inference
    emotion_target_size = emotion_classifier.input_shape[1:3]

        # loading images
    #rgb_image = load_image(image_path, grayscale=False, target_size=None)
    #print(type(rgb_image))
    #print(rgb_image.shape)
    #gray_image = load_image(image_path, grayscale=True, target_size=None)
    gray_image = image_bw_array
    gray_image = np.squeeze(gray_image)
    gray_image = gray_image.astype('uint8')

    faces = detect_faces(face_detection, gray_image)
    output={}
    for face_coordinates_,face_coordinates in enumerate(faces):

        x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
        gray_face = gray_image[y1:y2, x1:x2]

        try:
            gray_face = cv2.resize(gray_face, (emotion_target_size))
        except:
            continue

        # rgb_face = preprocess_input(rgb_face, False)
        # rgb_face = np.expand_dims(rgb_face, 0)

        gray_face = preprocess_input(gray_face, True)
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)
        emotion_label_arg = np.argmax(emotion_classifier.predict(gray_face))
        emotion_text = emotion_labels[emotion_label_arg]

            
        color = (255, 0, 0)

        draw_bounding_box(face_coordinates, rgb_image, color)
        
        draw_text(face_coordinates, rgb_image, emotion_text, color, 0, -50, 1, 2)

        output[face_coordinates_] = {'emotion': emotion_text, 'score': np.amax(emotion_classifier.predict(gray_face))}

    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    #print(type(bgr_image))
    cv2.imwrite('generated_images/predicted_test_image.png', bgr_image)

    def convert_floats(obj):
        if isinstance(obj, dict):
            return {k: convert_floats(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_floats(i) for i in obj]
        elif isinstance(obj, np.float32):
            return float(obj)
        return obj

    converted_data = convert_floats(output)

    # Convertir el diccionario a JSON
    output = json.dumps(converted_data)
    # Exportar el diccionario como un archivo JSON

    return output
    
if __name__ == '__main__':
    output = process()
    #print(output)
    