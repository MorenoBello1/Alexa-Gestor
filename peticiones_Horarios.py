from flask import Blueprint, request, render_template, jsonify
import gridfs
import os
import fitz  # PyMuPDF
import pytesseract
import tempfile
from PIL import Image
from io import BytesIO
from bson.objectid import ObjectId
from conexion import *

# Especificar la ruta a tesseract.exe si no está en el PATH del sistema

client, db, fs = connect_to_mongodb2()
horarios_ruta = Blueprint('horarios', __name__)

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
        db.horarios.insert_one({"nombre_docente": nombre_docente, "file_id": file_id, "filename": file.filename})

        return jsonify({"message": "File uploaded successfully", "file_id": str(file_id)}), 200

    else:
        return jsonify({"error": "Invalid file type"}), 400

@horarios_ruta.route('/api/docentes', methods=['GET'])
def get_docentes():
    docentes = db.horarios.distinct("nombre_docente")
    return jsonify({"docentes": [{"nombre": docente} for docente in docentes]}), 200

@horarios_ruta.route('/process/pdf/<doc_id>', methods=['GET'])
def process_pdf(doc_id):
    return