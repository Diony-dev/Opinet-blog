import os
from flask import Flask
from config import config

app = Flask(__name__)

# Usa la configuración de producción si la variable de entorno FLASK_ENV está en 'production'
if os.environ.get('FLASK_ENV') == 'production':
    app.config.from_object(config['production'])
else:
    app.config.from_object(config['develop'])

# Resto de tu código y rutas...

if __name__ == '__main__':
    app.run()