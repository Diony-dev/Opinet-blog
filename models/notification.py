# models/notification.py
from db import get_db
from datetime import datetime
from bson.objectid import ObjectId

class Notification:

    def __init__(self, data):
        self.id = str(data['_id'])
        self.user_id = data['user_id']
        self.message = data['message']
        self.is_read = data.get('is_read', False)
        self.id_post = data['id_post']
        self.timestamp = data.get('timestamp', datetime.utcnow())

    @staticmethod
    def create_notification(data):
        db = get_db()
        try:
            notification_data = {
                'user_id': ObjectId(data['user_id']),
                'message': data['message'],
                'id_post': ObjectId(data['post_id']),
                'is_read': False,
                'timestamp': datetime.utcnow()
            }
            print("Insertando notificación:", notification_data)
            result = db.notifications.insert_one(notification_data)
            print("Inserted ID:", result.inserted_id)
            if result.inserted_id:
                notification_data['_id'] = result.inserted_id
                return Notification(notification_data)
            return None
        except Exception as e:
            print(f"Error al crear notificación: {e}")
            return None

    @staticmethod
    def get_unread_notifications(user_id):
      """Obtiene las notificaciones no leídas de un usuario."""
      db = get_db()
      docs = db.notifications.find(
        {'user_id': ObjectId(user_id), 'is_read': False}
    ).sort('timestamp', -1)

      return [Notification(doc) for doc in docs]  # <- cada doc se convierte en objeto


    @staticmethod
    def mark_as_read(noti_id):
        """Marca una notificación como leída."""
        db = get_db()
        try:
            db.notifications.update_one({'_id': ObjectId(noti_id)}, {'$set': {'is_read': True}})
            return True
        except Exception as e:
            print(f"Error al marcar notificaciones como leídas: {e}")
            return False

    @staticmethod
    def count_unread_notifications(user_id):
        """Cuenta las notificaciones no leídas de un usuario."""
        db = get_db()
        return db.notifications.count_documents({'user_id': ObjectId(user_id), 'is_read': False})
