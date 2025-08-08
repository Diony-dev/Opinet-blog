# models/post.py
from bson.objectid import ObjectId
from db import get_db # Asumo que get_db() retorna la instancia de la base de datos (mongo.db)
import datetime # Importar para manejar fechas

class Post:
    def __init__(self, post_data):
        self.id = str(post_data['_id']) # ID como string para usar en URLs
        self.titulo = post_data['titulo']
        self.contenido = post_data['contenido']
        self.autor = post_data['autor'] # Nombre del autor
        self.fecha = post_data['fecha'] # Objeto datetime
        self.estado = post_data.get('estado', 'publicado') # Default to 'publicado' if not set

    @staticmethod
    def get_collection():
        """Retorna la colección 'posts'."""
        db = get_db()
        return db.Entradas # Asumo que tu colección se llama 'Entradas'

    @staticmethod
    def get_post(post_id):
        """
        Obtiene una entrada de blog por su ID.
        :param post_id: El ID (string) del post.
        :return: Una instancia de Post si se encuentra, None en caso contrario.
        """
        try:
            post_data = Post.get_collection().find_one({'_id': ObjectId(post_id)})
            if post_data:
                return Post(post_data) # Retorna una instancia de Post
            return None
        except Exception as e:
            print(f"Error al obtener post por ID {post_id}: {e}")
            return None

    @staticmethod
    def create_post(post_data):
        """
        Crea una nueva entrada de blog en la base de datos.
        :param post_data: Diccionario con los datos del post (titulo, contenido, autor, fecha, estado)
        :return: Una instancia de Post del post insertado si tiene éxito, None en caso contrario.
        """
        # Asegúrate de que 'fecha' sea un objeto datetime
        if not isinstance(post_data['fecha'], datetime.datetime):
            # Si no es datetime, podrías intentar convertirlo o usar la fecha actual
            post_data['fecha'] = datetime.datetime.utcnow() 
            
        try:
            result = Post.get_collection().insert_one(
                {
                    'titulo': post_data['titulo'],
                    'contenido': post_data['contenido'],
                    'autor': post_data['autor'],
                    'fecha': post_data['fecha'],
                    'email': post_data.get('email', None),  # Si necesitas almacenar el email del autor
                    'estado': post_data.get('estado', True)
                }
            )
            # Retornar el post recién creado
            return Post.get_post(str(result.inserted_id))
        except Exception as e:
            print(f"Error al crear el post: {e}")
            return None
    
    @staticmethod
    def get_all_posts(limit=None):
        """
        Obtiene todas las entradas de blog, ordenadas por fecha de creación descendente.
        :param limit: Número máximo de posts a retornar (opcional).
        :return: Una lista de instancias de Post.
        """
        try:
            query = Post.get_collection().find().sort("fecha", -1) # Ordenar por el campo 'fecha'
            if limit:
                query = query.limit(limit)
            
            posts = []
            for post_data in query:
                posts.append(Post(post_data)) # Crea instancias de Post
            return posts
        except Exception as e:
            print(f"Error al obtener todos los posts: {e}")
            return []

    @staticmethod
    def update_post(post_id, new_data):
        """
        Actualiza una entrada de blog existente.
        :param post_id: El ID (string) del post a actualizar.
        :param new_data: Diccionario con los campos a actualizar.
        :return: True si se actualizó, False en caso contrario.
        """
        try:
            obj_id = ObjectId(post_id)
            # No actualizamos 'fecha' aquí, solo los campos proporcionados en new_data
            result = Post.get_collection().update_one(
                {'_id': obj_id},
                {'$set': new_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error al actualizar post {post_id}: {e}")
            return False

    @staticmethod
    def delete_post(post_id):
        """
        Elimina una entrada de blog por su ID.
        :param post_id: El ID (string) del post a eliminar.
        :return: True si se eliminó, False en caso contrario.
        """
        try:
            obj_id = ObjectId(post_id)
            result = Post.get_collection().delete_one({'_id': obj_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error al eliminar post {post_id}: {e}")
            return False
        
    @staticmethod
    def get_posts_by_author(author_name, limit=None):
        """
        Obtiene todas las entradas de blog de un autor específico.
        :param author_name: Nombre del autor.
        :param limit: Número máximo de posts a retornar (opcional).
        :return: Una lista de instancias de Post.
        """
        try:
            query = Post.get_collection().find({'autor': author_name}).sort("fecha", -1)
            if limit:
                query = query.limit(limit)
            
            posts = []
            for post_data in query:
                posts.append(Post(post_data))
            return posts
        except Exception as e:
            print(f"Error al obtener posts por autor {author_name}: {e}")
            return []
        
    
    @staticmethod
    def get_posts_by_email(email, limit=None):
        """
        Obtiene todas las entradas de blog de un autor específico por su email.
        :param email: Email del autor.
        :param limit: Número máximo de posts a retornar (opcional).
        :return: Una lista de instancias de Post.
        """
        try:
            query = Post.get_collection().find({'email': email}).sort("fecha", -1)
            if limit:
                query = query.limit(limit)
            
            posts = []
            for post_data in query:
                posts.append(Post(post_data))
            return posts
        except Exception as e:
            print(f"Error al obtener posts por email {email}: {e}")
            return []
