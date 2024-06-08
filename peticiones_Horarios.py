from conexion import *
from flask import Blueprint, request, render_template
from flask import Flask, request, jsonify
import gridfs
import os
from pdf2image import convert_from_path
import pytesseract
import tempfile
import cv2
import numpy as np
import requests


client, db, fs = connect_to_mongodb2()
horarios_ruta = Blueprint('horarios', __name__)

# Ruta principal que renderiza un archivo HTML
@horarios_ruta.route('/horarios/')
def home():
    return render_template('Horarios.html')


@horarios_ruta.route('/upload/pdf', methods=['POST'])
def upload_pdf():
    if 'pdfFile' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['pdfFile']
    nombre_docente = request.form.get('nombreDocente')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not nombre_docente:
        return jsonify({"error": "No teacher name provided"}), 400

    if file and file.filename.endswith('.pdf'):
        file_id = fs.put(file, filename=file.filename)
        db.horarios.insert_one({"nombre_docente": nombre_docente, "file_id": file_id})

        return jsonify({"message": "File uploaded successfully", "file_id": str(file_id)}), 200

    else:
        return jsonify({"error": "Invalid file type"}), 400

@horarios_ruta.route('/api/docentes', methods=['GET'])
def get_docentes():
    docentes = db.horarios.distinct("nombre_docente")
    return jsonify({"docentes": [{"nombre": docente} for docente in docentes]}), 200

@horarios_ruta.route('/process/pdf/<filename>', methods=['GET'])
def process_pdf(filename):
    # Buscar el documento en la base de datos por el nombre del archivo
    documento = db.horarios.find_one({"nombre_docente": filename})
    if documento:
        file_id = documento["file_id"]
        # Obtener el archivo PDF desde GridFS
        grid_out = fs.get(file_id)
        temp_pdf_path = os.path.join(tempfile.gettempdir(), "temp.pdf")

        with open(temp_pdf_path, 'wb') as f:
            f.write(grid_out.read())

        # Convertir el PDF a imágenes
        pages = convert_from_path(temp_pdf_path)
        extracted_text = []

        for page in pages:
            # Usar pytesseract para extraer texto de cada imagen
            text = pytesseract.image_to_string(page, lang='spa')
            extracted_text.append(text)

        for idx, text in enumerate(extracted_text):
            print(f"Texto extraído de la página {idx + 1}:")
            print(text)
        # Procesar el texto extraído
        horarios_texto = interpretar_texto_horarios(extracted_text)
        
        # Procesar colores de las imágenes
        horarios_colores = interpretar_colores_horarios(pages)

        # Combinar los resultados
        horarios = combinar_resultados(horarios_texto, horarios_colores)
        
        print("Horarios extraídos:")
        print(horarios)
        return jsonify({"horarios": horarios}), 200
    else:
        return jsonify({"error": "File not found"}), 404

def interpretar_texto_horarios(texto_paginas):
    horarios = []
    dias_semana = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"]
    for texto in texto_paginas:
        lineas = texto.split('\n')
        dia_actual = None
        hora_actual = None
        for linea in lineas:
            # Identificar el día de la semana
            for dia in dias_semana:
                if dia in linea:
                    dia_actual = dia
                    break
            # Identificar la hora
            if any(char.isdigit() for char in linea):
                partes = linea.split()
                if "-" in partes[0]:  # Asumiendo que la primera parte es la hora
                    hora_actual = partes[0]
                    detalle = " ".join(partes[1:])
                else:
                    detalle = " ".join(partes)
                horario = {
                    "dia": dia_actual,
                    "hora": hora_actual,
                    "detalle": detalle
                }
                horarios.append(horario)
            else:
                # Si la línea no tiene dígitos, puede ser un detalle adicional
                if hora_actual and dia_actual:
                    horario = {
                        "dia": dia_actual,
                        "hora": hora_actual,
                        "detalle": linea
                    }
                    horarios.append(horario)
    return horarios

def interpretar_colores_horarios(pages):
    horarios = []
    for page in pages:
        # Convertir la página a un array numpy
        img = np.array(page)
        
        # Convertir la imagen de RGB a BGR (que es lo que usa OpenCV)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # Detectar colores específicos en la imagen
        colores = detectar_colores(img)
        
        for color, bounding_boxes in colores.items():
            for box in bounding_boxes:
                x, y, w, h = box
                detalle = pytesseract.image_to_string(img[y:y+h, x:x+w], lang='spa')
                horario = {
                    "color": color,
                    "detalle": detalle.strip()
                }
                horarios.append(horario)
    return horarios

def detectar_colores(img):
    # Definir rangos de colores en HSV
    colores = {
        "amarillo": ([20, 100, 100], [30, 255, 255]),
        # Añadir más colores si es necesario
    }
    
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    detecciones = {}
    
    for color, (lower, upper) in colores.items():
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")
        
        mask = cv2.inRange(img_hsv, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bounding_boxes = [cv2.boundingRect(c) for c in contours]
        detecciones[color] = bounding_boxes
        
    return detecciones

def combinar_resultados(horarios_texto, horarios_colores):
    # Combinar los resultados de texto y colores en una sola estructura de horarios
    # Aquí podrías usar lógica para mapear detalles de texto con colores específicos
    return {
        "texto": horarios_texto,
        "colores": horarios_colores
    }

