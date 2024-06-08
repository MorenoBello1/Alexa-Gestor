
# Configura la conexión a MongoDB Atlas
from pymongo import MongoClient
import gridfs

def connect_to_mongodb():
    try:
        client = MongoClient("mongodb+srv://arielmorenobelloj:105822moreno@cluster0.bthdnmq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        return client # Devuelve el cliente MongoDB, la base de datos y el sistema de archivos de la base de datos
    except Exception as e:
        print("Error al conectar a MongoDB Atlas:", e)
        return None

def connect_to_mongodb2():
    try:
        client = MongoClient("mongodb+srv://arielmorenobelloj:105822moreno@cluster0.bthdnmq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client.comunidades  # Nombre de tu base de datos
        fs = gridfs.GridFS(db)  # Inicializa GridFS con la base de datos
        return client, db, fs  # Devuelve el cliente MongoDB, la base de datos y el sistema de archivos de la base de datos
    except Exception as e:
        print("Error al conectar a MongoDB Atlas:", e)
        return None


