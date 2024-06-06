from flask import Blueprint,Flask, request, jsonify, render_template
from conexion import *

import uuid

comunidades_ruta = Blueprint('comunidades', __name__)

# Ruta principal que renderiza un archivo HTML
@comunidades_ruta.route('/comunidades/')
def ingreso_comunidades():
    return render_template('ingreso_comunidades.html')
# Ruta para manejar solicitudes GET a /api/data
@comunidades_ruta.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"mensaje": "Solicitud GET recibida"})

# Ruta para manejar solicitudes PUT a /api/data
@comunidades_ruta.route('/agregar/comunidad', methods=['PUT'])
def add_comunidad():
    data = request.get_json()
    print("Datos recibidos:", data)
    nombre_comunidad = data.get("nombre_comunidad")
    descripcion = data.get("descripcion")
    
    if not nombre_comunidad or not descripcion:
        print("Error: Faltan datos en la solicitud")
        return jsonify({"error": "Faltan datos"}), 400

    client = connect_to_mongodb()

    try:
        if client:
            print("Conexión exitosa a MongoDB")
            db = client.comunidades
            collection = db.activa
            
            # Generar un ID único
            comunidad_id = str(uuid.uuid4())

            comunidad = {
                "_id": comunidad_id,
                "nombre_comunidad": nombre_comunidad,
                "descripcion": descripcion
            }
            result = collection.insert_one(comunidad)
            print(f"Comunidad {nombre_comunidad} añadida con ID: {comunidad_id}")
            client.close()
            return jsonify({"mensaje": f"Comunidad {nombre_comunidad} añadida con éxito", "id": comunidad_id}), 200
        else:
            print("Error: No se pudo conectar a MongoDB Atlas")
            return jsonify({"error": "No se pudo conectar a MongoDB Atlas"}), 500
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500
    
@comunidades_ruta.route('/eliminar/comunidad/<nombre_comunidad>', methods=['DELETE'])
def delete_comunidad(nombre_comunidad):
    client = connect_to_mongodb()

    try:
        if client:
            print("Conexión exitosa a MongoDB")
            db = client.comunidades
            collection = db.activa
            
            result = collection.delete_one({"nombre_comunidad": nombre_comunidad})
            
            if result.deleted_count == 1:
                print(f"Comunidad con nombre: {nombre_comunidad} eliminada")
                client.close()
                return jsonify({"mensaje": f"Comunidad con nombre: {nombre_comunidad} eliminada con éxito"}), 200
            else:
                print(f"No se encontró la comunidad con nombre: {nombre_comunidad}")
                client.close()
                return jsonify({"error": f"No se encontró la comunidad con nombre: {nombre_comunidad}"}), 404
        else:
            print("Error: No se pudo conectar a MongoDB Atlas")
            return jsonify({"error": "No se pudo conectar a MongoDB Atlas"}), 500
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@comunidades_ruta.route('/api/comunidades', methods=['GET'])
def obtener_comunidades():
    try:
        client = connect_to_mongodb()
        db = client.comunidades
        collection = db.activa

        # Excluir el campo "_id" de los resultados
        resultados = collection.find({}, {"_id": 0})

        # Convertir los resultados a una lista de diccionarios
        comunidades = [comunidad for comunidad in resultados]

        # Cerrar la conexión con MongoDB
        client.close()

        # Devolver los resultados como JSON
        return jsonify({"comunidades": comunidades}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Manejo de errores 404 (No encontrado)
@comunidades_ruta.errorhandler(404)
def not_found(error):
    return jsonify({"error": "No encontrado"}), 404

# Manejo de errores 500 (Error interno del servidor)
@comunidades_ruta.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

# Si el script se ejecuta directamente, inicia el servidor de desarrollo de Flask
