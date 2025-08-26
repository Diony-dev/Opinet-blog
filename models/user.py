# src/models/user.py
from flask_login import UserMixin
from bson.objectid import ObjectId
import re
from db import get_db
from flask import current_app
from itsdangerous import URLSafeTimedSerializer 

class User(UserMixin):
    # Constructor de la clase
    def __init__(self, user_data):
        # Usamos .get() para evitar KeyErrors y manejar campos faltantes
        # A diferencia del error anterior, este usa user_data.get() de forma
        # segura para cualquier dato que no se obtenga en la consulta.
        self.id = str(user_data.get('_id'))
        self.nombre = user_data.get('nombre')
        self.email = user_data.get('email')
        self.password = user_data.get('pasw') # Asume que 'pasw' es el nombre de la clave en la DB
        self.foto = user_data.get('foto', None)

    @staticmethod
    def get_user(user_id):
        """Busca un usuario por su ObjectId y devuelve un objeto User."""
        db = get_db()
        user_data = db.Usuarios.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def get_user_by_email(email):
        """Busca un usuario por su email y devuelve un objeto User."""
        db = get_db()
        user_data = db.Usuarios.find_one({'email': email})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def create_user(user_data):
        """Crea un nuevo usuario en la base de datos."""
        db = get_db()
        id_user = db.Usuarios.insert_one({
            'nombre': user_data['nombre'],
            'email': user_data['email'],
            'pasw': user_data['pasw'],
            'foto': user_data.get('foto', None)
        }).inserted_id
        return User.get_user(str(id_user))

    @staticmethod
    def update_user(user_id, user_data):
        """Actualiza la información de un usuario."""
        db = get_db()
        update_data = {
            'nombre': user_data['nombre'],
            'email': user_data['email'],
            'foto': user_data.get('foto', None)
        }
        db.Usuarios.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
        return User.get_user(user_id)

    @staticmethod
    def update_pass(user_id, new_password):
        db = get_db()
        db.Usuarios.update_one({'_id': ObjectId(user_id)}, {'$set': {'pasw': new_password}})
        return User.get_user(user_id)

    @staticmethod
    def search_by_name(query):
        """
        Busca usuarios en la base de datos por nombre de forma insensible a mayúsculas.
        """
        db = get_db()
        if not query:
            return []

        # Crea una expresión regular para una búsqueda flexible
        search_regex = re.compile(f".*{re.escape(query)}.*", re.IGNORECASE)

        # Realiza la búsqueda en la colección 'Usuarios'
        found_users_data = db.Usuarios.find(
            {"nombre": search_regex},
            # Proyecta solo los campos necesarios, '_id' siempre se incluye
            {"nombre": 1, "foto": 1}
        )

        # Convierte los documentos encontrados en objetos de la clase User
        return [User(user_data) for user_data in found_users_data]
    

    
    def generate_reset_token(self, expires_sec=3600):
       s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
       return s.dumps({'user_id': str(self.id)}, salt='password-reset-salt')

    @staticmethod
    def verify_token(token, max_age=3600):
       s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
       try:
           data = s.loads(token, salt='password-reset-salt', max_age=max_age)
           user_id = data['user_id']
       except Exception:
           return None
       return User.get_user(user_id)