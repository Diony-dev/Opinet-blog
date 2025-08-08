from flask_login import UserMixin
from bson.objectid import ObjectId

from db import get_db



class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.nombre= user_data['nombre']
        self.email = user_data['email']
        self.password = user_data['pasw']
        self.foto = user_data.get('foto', None)

    @staticmethod
    def get_user(user_id):
        db = get_db()
        user_data = db.Usuarios.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None
    
    @staticmethod
    def get_user_by_email(email):
        db = get_db()
        user_data = db.Usuarios.find_one({'email': email})
        if user_data:
            return User(user_data)
        return None
    
    @staticmethod
    def create_user(user_data):
        db = get_db()
        id_user = db.Usuarios.insert_one({
            'nombre':user_data['nombre'],
            'email': user_data['email'],
            'pasw': user_data['pasw'],
            'foto': user_data.get('foto', None)
        }).inserted_id
        return User.get_user(str(id_user))
    
    @staticmethod
    def update_user(user_id, user_data):
        db = get_db()
        update_data = {
            'nombre': user_data['nombre'],
            'email': user_data['email'],
            'foto': user_data.get('foto', None)
        }
        db.Usuarios.update_one({'_id':ObjectId(user_id)}, {'$set': update_data})
        return User.get_user(user_id)
    
