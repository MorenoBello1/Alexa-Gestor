from flask import Blueprint,Flask, request, jsonify, render_template
from conexion import *
from bson import ObjectId
import uuid

formatos_ruta = Blueprint('formatos', __name__)

# Ruta principal que renderiza un archivo HTML
@formatos_ruta.route('/formatos/')
def home():
    return render_template('Formatos.html')

# Ruta para manejar solicitudes PUT a /api/data
@formatos_ruta.route('/agregar/formato', methods=['PUT'])
def add_formato():
    data = request.get_json()
    print("Datos recibidos:", data)
    nombre_formato = data.get("nombre_formato")
    fecha_actualizacion = data.get("fecha_actualizacion")
    observacion = data.get("observacion")
    carrera_id = data.get("carrera_id") 

    
    if not nombre_formato or not fecha_actualizacion or not observacion or not carrera_id:
        print("Error: Faltan datos en la solicitud")
        return jsonify({"error": "Faltan datos"}), 400

    client = connect_to_mongodb()

    try:
        if client:
            print("Conexión exitosa a MongoDB")
            db = client.AlexaGestor
            collection_formatos = db.formatos
            collection_carreras = db.carreras
            
            # Verificar existencia de id_carrera en la colección carreras
            carrera = collection_carreras.find_one({"_id": carrera_id})
            if not carrera:
                print("Error: id_carrera no existe")
                return jsonify({"error": "id_carrera no existe"}), 400
            
            # Generar un ID único para la comunidad
            formato_id = str(uuid.uuid4())

            # Crear el documento para insertar
            formatos = {
                "_id": formato_id,
                "nombre_formato": nombre_formato,
                "fecha_actualizacion": fecha_actualizacion,
                "observacion": observacion,
                "carrera_id": carrera_id,
             }
            
            # Insertar el documento en la colección
            result = collection_formatos.insert_one(formatos)
            print("Comunidad agregada con ID:", formato_id)
            return jsonify({"mensaje": "Formato agregada exitosamente", "formato_id": formato_id}), 201
    except Exception as e:
        print("Error al conectar o insertar en MongoDB:", str(e))
        return jsonify({"error": "Error al conectar o insertar en MongoDB"}), 500
    finally:
        client.close()
    
@formatos_ruta.route('/eliminar/formato/<_id>', methods=['DELETE'])
def delete_formato(_id):
    client = connect_to_mongodb()
    try:
        db = client.AlexaGestor
        collection = db.formatos
        result = collection.delete_one({"_id": _id})
        if result.deleted_count == 1:
            return jsonify({"mensaje": f"Horario con id: {_id} eliminado con éxito"}), 200
        else:
            return jsonify({"error": f"No se encontró el horario con id: {_id}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        client.close()
    
@formatos_ruta.route('/api/formatos', methods=['GET'])
def obtener_formatos():
    client = connect_to_mongodb()
    try:
        db = client.AlexaGestor
        collection_formatos= db.formatos
        collection_carreras = db.carreras

        formatos = list(collection_formatos.find({}))
        
        for formato in formatos:
            carrera_id = formato.get("carrera_id")
            
            carrera = collection_carreras.find_one({"_id": carrera_id}, {"_id": 0, "nombre_carrera": 1})
            
            formato["nombre_carrera"] = carrera["nombre_carrera"] if carrera else "Desconocido"
        
        return jsonify({"formatos": formatos}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        client.close()

# Manejo de errores 404 (No encontrado)
@formatos_ruta.errorhandler(404)
def not_found(error):
    return jsonify({"error": "No encontrado"}), 404

# Manejo de errores 500 (Error interno del servidor)
@formatos_ruta.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

# Si el script se ejecuta directamente, inicia el servidor de desarrollo de Flask
