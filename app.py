from flask import Flask
from peticiones_Com import comunidades_ruta
from peticiones_home import home_ruta
from peticiones_Horarios import horarios_ruta
from peticiones_Eventos import eventos_ruta

import numpy as np
from bson.objectid import ObjectId


app = Flask(__name__)

# Registrar los Blueprints en la aplicación principal
app.register_blueprint(home_ruta)
app.register_blueprint(comunidades_ruta)
app.register_blueprint(horarios_ruta)
app.register_blueprint(eventos_ruta)



if __name__ == '__main__':
    app.run(debug=True, port=8080)