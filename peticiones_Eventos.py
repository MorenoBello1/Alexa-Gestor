from flask import Blueprint,Flask, request, jsonify, render_template
from conexion import *

import uuid



eventos_ruta = Blueprint('eventos', __name__)

# Ruta principal que renderiza un archivo HTML
@eventos_ruta.route('/eventos/')
def home():
    return render_template('Eventos.html')

# Ruta para manejar solicitudes GET a /api/data
@eventos_ruta.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"mensaje": "Solicitud GET recibida"})

# Ruta para manejar solicitudes PUT a /api/data
@eventos_ruta.route('/agregar/evento', methods=['PUT'])
def add_evento():
    data = request.get_json()
    print("Datos recibidos:", data)
    nombre_evento = data.get("nombre_evento")
    descripcion = data.get("descripcion")
    
    if not nombre_evento or not descripcion:
        print("Error: Faltan datos en la solicitud")
        return jsonify({"error": "Faltan datos"}), 400

    client = connect_to_mongodb()

    try:
        if client:
            print("Conexión exitosa a MongoDB")
            db = client.comunidades
            collection = db.eventos
            
            # Generar un ID único
            evento_id = str(uuid.uuid4())

            evento = {
                "_id": evento_id,
                "nombre_evento": nombre_evento,
                "descripcion": descripcion
            }
            result = collection.insert_one(evento)
            print(f"Evento {nombre_evento} añadida con ID: {evento_id}")
            client.close()
            return jsonify({"mensaje": f"Evento {nombre_evento} añadida con éxito", "id": evento_id}), 200
        else:
            print("Error: No se pudo conectar a MongoDB Atlas")
            return jsonify({"error": "No se pudo conectar a MongoDB Atlas"}), 500
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500
    
@eventos_ruta.route('/eliminar/evento/<nombre_evento>', methods=['DELETE'])
def delete_evento(nombre_evento):
    client = connect_to_mongodb()

    try:
        if client:
            print("Conexión exitosa a MongoDB")
            db = client.comunidades
            collection = db.eventos
            
            result = collection.delete_one({"nombre_evento": nombre_evento})
            
            if result.deleted_count == 1:
                print(f"Evento con nombre: {nombre_evento} eliminada")
                client.close()
                return jsonify({"mensaje": f"Evento con nombre: {nombre_evento} eliminada con éxito"}), 200
            else:
                print(f"No se encontró el evento con nombre: {nombre_evento}")
                client.close()
                return jsonify({"error": f"No se encontró la comunidad con nombre: {nombre_evento}"}), 404
        else:
            print("Error: No se pudo conectar a MongoDB Atlas")
            return jsonify({"error": "No se pudo conectar a MongoDB Atlas"}), 500
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@eventos_ruta.route('/api/eventos', methods=['GET'])
def obtener_eventos():
    try:
        client = connect_to_mongodb()
        db = client.comunidades
        collection = db.eventos

        # Excluir el campo "_id" de los resultados
        resultados = collection.find({}, {"_id": 0})

        # Convertir los resultados a una lista de diccionarios
        eventos = [evento for evento in resultados]

        # Cerrar la conexión con MongoDB
        client.close()

        # Devolver los resultados como JSON
        return jsonify({"eventos": eventos}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Manejo de errores 404 (No encontrado)
@eventos_ruta.errorhandler(404)
def not_found(error):
    return jsonify({"error": "No encontrado"}), 404

# Manejo de errores 500 (Error interno del servidor)
@eventos_ruta.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

# Si el script se ejecuta directamente, inicia el servidor de desarrollo de Flask
