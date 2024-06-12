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
    
    # Extraer los campos del JSON recibido
    nombre_comunidad = data.get("nombre_comunidad")
    periodo_comunidad = data.get("periodo_comunidad")
    ubicacion_comunidad = data.get("ubicacion_comunidad")
    observaciones = data.get("observaciones")
    carrera_id = data.get("carrera_id")
    docente_id = data.get("docente_id")
    campos_faltantes = []
    if not nombre_comunidad:
        campos_faltantes.append("nombre_comunidad")
    if not periodo_comunidad:
        campos_faltantes.append("periodo_comunidad")
    if not ubicacion_comunidad:
        campos_faltantes.append("ubicacion_comunidad")
    if not observaciones:
        campos_faltantes.append("observaciones")
    if not carrera_id:
        campos_faltantes.append("id_carrera")
    if not docente_id:
        campos_faltantes.append("id_docente")
    
    if campos_faltantes:
        print("Error: Faltan datos en la solicitud. Campos faltantes:", campos_faltantes)
        return jsonify({"error": "Faltan datos", "campos_faltantes": campos_faltantes}), 400
    # Validar que todos los campos requeridos estén presentes
    if not nombre_comunidad or not periodo_comunidad or not ubicacion_comunidad or not carrera_id or not docente_id:
        print("Error: Faltan datos en la solicitud")
        return jsonify({"error": "Faltan datos"}), 400

    # Conectar a MongoDB
    client = connect_to_mongodb()

    try:
        if client:
            print("Conexión exitosa a MongoDB")
            db = client.AlexaGestor
            collection_comunidades = db.comunidades
            collection_docentes = db.docentes
            collection_carreras = db.carreras
            
            # Verificar existencia de id_docente en la colección docentes
            docente = collection_docentes.find_one({"_id": docente_id})
            if not docente:
                print("Error: id_docente no existe")
                return jsonify({"error": "id_docente no existe"}), 400
            
            # Verificar existencia de id_carrera en la colección carreras
            carrera = collection_carreras.find_one({"_id": carrera_id})
            if not carrera:
                print("Error: id_carrera no existe")
                return jsonify({"error": "id_carrera no existe"}), 400
            
            # Generar un ID único para la comunidad
            comunidad_id = str(uuid.uuid4())

            # Crear el documento para insertar
            comunidad = {
                "_id": comunidad_id,
                "nombre_comunidad": nombre_comunidad,
                "periodo_comunidad": periodo_comunidad,
                "ubicacion_comunidad": ubicacion_comunidad,
                "observaciones": observaciones,
                "carrera_id": carrera_id,
                "docente_id": docente_id
             }
            
            # Insertar el documento en la colección
            result = collection_comunidades.insert_one(comunidad)
            print("Comunidad agregada con ID:", comunidad_id)
            return jsonify({"mensaje": "Comunidad agregada exitosamente", "comunidad_id": comunidad_id}), 201
    except Exception as e:
        print("Error al conectar o insertar en MongoDB:", str(e))
        return jsonify({"error": "Error al conectar o insertar en MongoDB"}), 500
    finally:
        client.close()
    
@comunidades_ruta.route('/eliminar/comunidad/<nombre_comunidad>', methods=['DELETE'])
def delete_comunidad(nombre_comunidad):
    client = connect_to_mongodb()

    try:
        if client:
            print("Conexión exitosa a MongoDB")
            db = client.AlexaGestor
            collection = db.comunidades
            
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
    client = connect_to_mongodb()
    try:
        db = client.AlexaGestor
        collection_comunidades = db.comunidades
        collection_docentes = db.docentes
        collection_carreras = db.carreras

        comunidades = list(collection_comunidades.find({}))
        
        for comunidad in comunidades:
            docente_id = comunidad.get("docente_id")
            carrera_id = comunidad.get("carrera_id")
            
            docente = collection_docentes.find_one({"_id": docente_id}, {"_id": 0, "nombre_docente": 1, "apellido_docente": 1})
            carrera = collection_carreras.find_one({"_id": carrera_id}, {"_id": 0, "nombre_carrera": 1})
            
            comunidad["nombre_docente"] = f"{docente['nombre_docente']} {docente['apellido_docente']}" if docente else "Desconocido"
            comunidad["nombre_carrera"] = carrera["nombre_carrera"] if carrera else "Desconocido"
        
        return jsonify({"comunidades": comunidades}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        client.close()

# Manejo de errores 404 (No encontrado)
@comunidades_ruta.errorhandler(404)
def not_found(error):
    return jsonify({"error": "No encontrado"}), 404

# Manejo de errores 500 (Error interno del servidor)
@comunidades_ruta.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

# Si el script se ejecuta directamente, inicia el servidor de desarrollo de Flask
