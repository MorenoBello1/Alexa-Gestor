from flask import Blueprint, Flask, request, jsonify, render_template
from conexion import *
import uuid
import os

horarios_ruta = Blueprint('horarios', __name__)

@horarios_ruta.route('/horarios/')
def ingreso_comunidades():
    return render_template('Horarios.html')

@horarios_ruta.route('/agregar/horario', methods=['POST'])
def add_horario():
    try:
        periodo_horario = request.form.get("periodo_horario")
        docente_id = request.form.get("docente_id")
        imagen_horario = request.files.get("imagen_horario")

        if not periodo_horario or not docente_id or not imagen_horario:
            return jsonify({"error": "Faltan datos"}), 400

        # Conectar a MongoDB
        client = connect_to_mongodb()
        db = client.AlexaGestor
        collection_horarios = db.horarios
        collection_docentes = db.docentes

        # Verificar si el docente existe
        docente = collection_docentes.find_one({"_id": docente_id})
        if not docente:
            client.close()
            return jsonify({"error": "El id_docente no existe"}), 400

        # Guardar la imagen en MongoDB
        horario_id = str(uuid.uuid4())
        imagen_data = imagen_horario.read()  # Leer los datos de la imagen
        imagen_mime_type = imagen_horario.mimetype  # Obtener el tipo MIME de la imagen

        # Crear el documento para insertar en MongoDB
        horario = {
            "_id": horario_id,
            "periodo_horario": periodo_horario,
            "imagen_horario": imagen_data,  # Guardamos los datos de la imagen en MongoDB
            "imagen_mime_type": imagen_mime_type,  # Guardamos el tipo MIME de la imagen
            "docente_id": docente_id
        }

        # Insertar el documento en la colección de horarios
        collection_horarios.insert_one(horario)

        client.close()

        return jsonify({"mensaje": "Horario agregado exitosamente", "horario_id": horario_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@horarios_ruta.route('/eliminar/horario/<_id>', methods=['DELETE'])
def delete_horario(_id):
    client = connect_to_mongodb()
    try:
        db = client.AlexaGestor
        collection = db.horarios
        result = collection.delete_one({"_id": _id})
        if result.deleted_count == 1:
            return jsonify({"mensaje": f"Horario con id: {_id} eliminado con éxito"}), 200
        else:
            return jsonify({"error": f"No se encontró el horario con id: {_id}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        client.close()

import base64

@horarios_ruta.route('/api/horarios', methods=['GET'])
def obtener_horarios():
    client = connect_to_mongodb()
    try:
        db = client.AlexaGestor
        collection_horarios = db.horarios
        collection_docentes = db.docentes

        horarios = list(collection_horarios.find({}))
        for horario in horarios:
            docente_id = horario.get("docente_id")
            docente = collection_docentes.find_one({"_id": docente_id}, {"_id": 0, "nombre_docente": 1, "apellido_docente": 1})
            if docente:
                horario["nombre_docente"] = f"{docente['nombre_docente']} {docente['apellido_docente']}"
            else:
                horario["nombre_docente"] = "Desconocido"
            
            # Convertir imagen_horario a base64
            imagen_data = horario.get("imagen_horario")
            if imagen_data:
                horario["imagen_horario"] = base64.b64encode(imagen_data).decode('utf-8')
        
        return jsonify({"horarios": horarios}), 200
    except Exception as e:
        print(f"Error en obtener_horarios(): {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        client.close()

