
# Configura la conexión a MongoDB Atlas
from pymongo import MongoClient

def connect_to_mongodb():
    try:
        client = MongoClient("mongodb+srv://arielmorenobelloj:105822moreno@cluster0.bthdnmq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        #print("Conexion Exitosa")
        return client  # Devuelve el cliente MongoDB
    except Exception as e:
        print("Error al conectar a MongoDB Atlas:", e)
        return None

# Método para añadir una comunidad a la base de datos
