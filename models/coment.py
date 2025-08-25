from bson.objectid import ObjectId
from db import get_db
from datetime import datetime

class Coment:
    def __init__(self, coment_data):
        self.id = str(coment_data['_id'])
        self.contenido = coment_data['contenido']
        self.id_post = coment_data['id_post']
        self.autor = coment_data['autor']
        self.fecha = coment_data['fecha']
        self.parent_id = ObjectId(coment_data.get('parent_id')) if coment_data.get('parent_id') else None

    @staticmethod
    def create_coment(coment_data):
        """
        Crea un nuevo comentario en la base de datos.
        :param coment_data: Diccionario con los datos del comentario (contenido, id_post, autor, fecha)
        :return: Una instancia de Coment del comentario insertado si tiene éxito, None en caso contrario.
        """
        db = get_db()
        if not isinstance(coment_data['fecha'], datetime):
            coment_data['fecha'] = datetime.utcnow()
        try:
            result = db.Comentarios.insert_one(
                {
                    'contenido':coment_data['contenido'],
                    'id_post': ObjectId(coment_data['id_post']),
                    'autor': coment_data['autor'],
                    'fecha': coment_data['fecha'],
                    'parent_id':ObjectId(coment_data.get('parent_id')) if coment_data.get('parent_id') else None
                }
            ).inserted_id
            coment_data['_id'] = result
            return Coment(coment_data)
        
        except Exception as e:
            print(f"Error al crear comentario: {e}")
            return None
        
    @staticmethod
    def get_coments_by_post(post_id):
        """
        Obtiene todos los comentarios de un post específico.
        :param post_id: El ID del post del cual se quieren obtener los comentarios.
        :return: Una lista de instancias de Coment.
        """
        db = get_db()
        coments_data = db.Comentarios.find({'id_post': ObjectId(post_id)}).sort('fecha', -1)
        comentarios = [Coment(coment) for coment in coments_data]
       
       #organizamos las jerarquia
        comentarios_dict = {c.id: c for c in comentarios}
        root_comentarios = []
        for c in comentarios:
            if c.parent_id:
                parent = comentarios_dict.get(str(c.parent_id))
                if not hasattr(parent,'replies'):
                    parent.replies = []
                parent.replies.append(c)
            else:
                root_comentarios.append(c)

        return root_comentarios